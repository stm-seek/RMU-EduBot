"""API ผู้ดูแลกิจกรรมนักศึกษา"""
from __future__ import annotations
from typing import Annotated
import json
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from .config import Settings, get_settings
from .admin import require_admin, _http_error
from . import activities
from .db import SupportsExecute, SupportsQuery

router = APIRouter(prefix="/api/admin/activities", tags=["admin-activities"])
SettingsDep = Annotated[Settings, Depends(get_settings)]

def _db(write=False):
    from .main import get_db
    db = get_db()
    if db is None or (write and not isinstance(db, SupportsExecute)) or (not write and not isinstance(db, SupportsQuery)):
        raise _http_error(503, "ฐานข้อมูลยังไม่พร้อม — ลองอีกครั้งในอีกสักครู่")
    return db

class ActivityPatch(BaseModel):
    is_active: bool | None = None
    is_pinned: bool | None = None
    admin_note: str | None = Field(default=None, max_length=2000)

class ManualActivity(BaseModel):
    source_ref: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=500)
    detail_url: str | None = None
    register_status: str = "open"
    register_dates_text: str | None = None
    event_dates_text: str | None = None
    organizer: str | None = None
    hours_text: str | None = None
    capacity: int | None = None
    applied: int | None = None

@router.get("")
async def list_activities(request: Request, settings: SettingsDep, register_status: str | None = None, q: str | None = None):
    require_admin(request, settings)
    clauses, params = ["1=1"], []
    if register_status: clauses.append("register_status=%s"); params.append(register_status)
    if q: clauses.append("title ILIKE %s"); params.append(f"%{q}%")
    rows = await _db().fetch_all(f"SELECT * FROM activities WHERE {' AND '.join(clauses)} ORDER BY is_pinned DESC, register_end ASC NULLS LAST, activity_id DESC", params)
    return {"rows": rows}

@router.patch("/{activity_id}")
async def patch_activity(activity_id: int, payload: ActivityPatch, request: Request, settings: SettingsDep):
    admin = require_admin(request, settings)
    changes = payload.model_dump(exclude_none=True)
    if not changes: return {"ok": True, "changes": {}}
    sets = ",".join(f"{key}=%s" for key in changes)
    params = [*changes.values(), admin, activity_id]
    await _db(True).execute(f"UPDATE activities SET {sets}, updated_by=%s WHERE activity_id=%s", params)
    await _db(True).execute("INSERT INTO admin_audit_logs (admin_username, action, table_name, row_key, changes) VALUES (%s,%s,%s,%s,%s::jsonb)", (admin, "update", "activities", str(activity_id), json.dumps(changes, ensure_ascii=False)))
    return {"ok": True, "changes": changes}

@router.post("")
async def create_manual(payload: ManualActivity, request: Request, settings: SettingsDep):
    admin = require_admin(request, settings)
    row = payload.model_dump(); row.update(source="manual", updated_by=admin)
    await activities.upsert_activity(_db(True), row)
    return {"ok": True, "source": "manual", "source_ref": payload.source_ref}

@router.post("/scrape")
async def scrape_now(request: Request, settings: SettingsDep):
    admin = require_admin(request, settings)
    db = _db(True)
    running = await db.fetch_one("SELECT run_id FROM activity_scrape_runs WHERE status='running' ORDER BY started_at DESC LIMIT 1")
    if running: raise _http_error(409, "มีรอบดึงข้อมูลกำลังทำงานอยู่")
    run = await db.fetch_one("INSERT INTO activity_scrape_runs (status, triggered_by) VALUES ('running', %s) RETURNING run_id", (f"admin:{admin}",))
    try:
        from .main import get_http
        result = await activities.scrape_activities(db, get_http(), triggered_by=f"admin:{admin}")
        await db.execute("UPDATE activity_scrape_runs SET status='ok', finished_at=now(), http_status=%s, bytes=%s, rows_found=%s, rows_inserted=%s, details_fetched=%s WHERE run_id=%s", (result["http_status"], result["bytes"], result["rows_found"], result["rows_found"], result["details_fetched"], run["run_id"]))
        return {"ok": True, "run_id": run["run_id"], **result}
    except Exception as exc:
        await db.execute("UPDATE activity_scrape_runs SET status='failed', finished_at=now(), error=%s WHERE run_id=%s", (str(exc)[:1000], run["run_id"]))
        raise _http_error(502, "ดึงข้อมูลกิจกรรมไม่สำเร็จ") from exc

@router.get("/runs")
async def scrape_runs(request: Request, settings: SettingsDep):
    require_admin(request, settings)
    rows = await _db().fetch_all("SELECT * FROM activity_scrape_runs ORDER BY started_at DESC LIMIT 50")
    latest = rows[0].get("finished_at") if rows else None
    return {"rows": rows, "latest_finished_at": latest}
