"""
เทสสคริปต์อัปเดต Rich Menu — ยิงใส่ "LINE ปลอม" ที่เก็บสถานะในหน่วยความจำ

ทำไมไฟล์นี้ต้องมี: สคริปต์นี้ **สร้างและลบเมนูจริง** ถ้าลำดับผิด (ลบก่อนตั้ง
default) ผู้ใช้จะไม่เหลือเมนูเลย และการยิง LINE จริงซ้ำ ๆ ไม่ได้เพราะโควตา
สร้าง/ลบ 100 ครั้ง/ชั่วโมง — เทสจึงต้องตรึง *ลำดับคำสั่ง* ไว้แทน

สิ่งที่ยึดไว้ในไฟล์นี้

* เมนูที่ตรงกับโค้ดแล้ว → ไม่ยิงคำสั่งเขียนใด ๆ เลย (ไม่เปลืองโควตา)
* เมนูเก่า → สร้างใหม่ + อัปโหลดภาพ + **ตั้ง default ก่อน แล้วจึงลบใบเก่า**
* ช่องเหมือนแต่ภาพต่าง (เคสที่เทียบแค่ ``data`` จะพลาด) → ต้องอัปเดต
* ใบที่ตรงอยู่แล้วค้างบน channel → ตั้ง default ให้ ไม่สร้างใบซ้ำ
* ``--prune`` ลบของเก่าที่ชื่อเดียวกับเมนูหลัก แต่ไม่แตะใบโหมดปรึกษา
* ``--check`` / ``--dry-run`` ไม่แก้อะไร และคืน exit code ให้เอาไปต่อได้
* ไม่มี terminal ให้ถามยืนยัน = ไม่แก้อะไร (ต้องสั่ง ``--yes`` เท่านั้น)
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.config import REPO_ROOT
from app.line import rich_menu as rm

from scripts import update_rich_menu

# ภาพจริงใน repo — สคริปต์เทียบ md5 กับไบต์ชุดนี้
IMAGE = Path(REPO_ROOT, "assets", "rich_menu.png").read_bytes()
OLD_IMAGE = b"bytes-of-the-previous-menu-image"

CONSULT_ID = "richmenu-consult"

# เมนูก่อน commit da9c2bf: กู้ยืม กยศ. / ทำอะไรได้บ้าง ยังอยู่ และไม่มี
# วางแผนการเรียน/วางแผนเกรด — เคสจริงที่ users เห็นเมนูเก่าอยู่
OLD_SLOTS = (
    ("ปรึกษา AI", "ai_session"),
    ("กู้ยืม กยศ.", "loan"),
    ("ติดต่ออาจารย์", "instructors"),
    ("ค้นรายวิชา", "course"),
    ("เอกสาร/คำร้อง", "documents"),
    ("ทำอะไรได้บ้าง", "menu"),
)


class FakeResponse:
    """response ปลอม — เลียนแบบ httpx เฉพาะ field ที่สคริปต์ใช้"""

    def __init__(self, status_code: int, payload: dict | None = None, content: bytes = b""):
        self.status_code = status_code
        self._payload = payload or {}
        # httpx ใส่ body จริงมาด้วยเสมอ และ ``expect_ok`` ในสคริปต์เช็ค
        # ``response.content`` ก่อนจะเรียก ``.json()`` — เลียนให้ตรง ไม่งั้น
        # สคริปต์จะเห็นเป็น body ว่าง
        self.content = content or (
            json.dumps(self._payload).encode("utf-8") if self._payload else b""
        )
        self.text = str(self._payload)

    def json(self) -> dict:
        return self._payload


class FakeLine:
    """
    LINE ปลอม — เก็บเมนู/ภาพ/default ไว้ในหน่วยความจำ แล้วบันทึกทุกคำสั่ง

    ``calls`` เก็บ ``(ชื่อคำสั่ง, id)`` เพื่อยืนยัน **ลำดับ** ของการเขียน
    (สร้าง → อัปโหลด → ตั้ง default → ลบใบเก่า) ซึ่งเป็นหัวใจของสคริปต์นี้
    """

    def __init__(self, menus=None, default_id=None, image=OLD_IMAGE):
        self.menus = {item["richMenuId"]: item for item in (menus or [])}
        self.images = {menu_id: image for menu_id in self.menus}
        self.default_id = default_id
        self.calls: list[tuple[str, str]] = []
        self._seq = 0

    def __enter__(self) -> "FakeLine":
        return self

    def __exit__(self, *exc) -> bool:
        return False

    def get(self, url: str) -> FakeResponse:
        self.calls.append(("get", url.rsplit("/", 1)[-1]))
        if url.endswith("/user/all/richmenu"):
            if self.default_id is None:
                return FakeResponse(404, {"message": "Not found"})
            return FakeResponse(200, {"richMenuId": self.default_id})

        tail = url.rsplit("/richmenu/", 1)[-1]
        if tail == "list":
            return FakeResponse(200, {"richmenus": list(self.menus.values())})
        if tail.endswith("/content"):
            menu_id = tail[: -len("/content")]
            if menu_id not in self.images:
                return FakeResponse(404, {"message": "Not found"})
            return FakeResponse(200, content=self.images[menu_id])
        return FakeResponse(200, self.menus[tail])

    def post(self, url, json=None, content=None, headers=None) -> FakeResponse:
        if url.endswith("/richmenu"):  # สร้างเมนู
            self._seq += 1
            menu_id = f"richmenu-new{self._seq}"
            # LINE ใส่ richMenuId กลับมาในตอน list เสมอ (body ที่ส่งไปไม่มี field นี้)
            self.menus[menu_id] = {**json, "richMenuId": menu_id}
            self.calls.append(("create", menu_id))
            return FakeResponse(200, {"richMenuId": menu_id})
        if "/user/all/richmenu/" in url:  # ตั้ง default
            menu_id = url.rsplit("/", 1)[-1]
            self.default_id = menu_id
            self.calls.append(("set_default", menu_id))
            return FakeResponse(200)
        if url.endswith("/content"):  # อัปโหลดภาพ (โดเมน api-data)
            menu_id = url.rsplit("/richmenu/", 1)[-1][: -len("/content")]
            self.images[menu_id] = content
            self.calls.append(("upload", menu_id))
            return FakeResponse(200)
        raise AssertionError(f"ไม่รู้จัก POST {url}")

    def delete(self, url: str) -> FakeResponse:
        menu_id = url.rsplit("/", 1)[-1]
        self.menus.pop(menu_id, None)
        self.images.pop(menu_id, None)
        self.calls.append(("delete", menu_id))
        return FakeResponse(200)

    @property
    def writes(self) -> list[tuple[str, str]]:
        """คำสั่งที่ไม่ใช่การอ่าน — ใช้ยืนยันว่า "ไม่แตะอะไรเลย" """
        return [call for call in self.calls if call[0] != "get"]


def menu(menu_id: str, slots, name: str = rm.MENU_NAME) -> dict:
    """นิยามเมนูหน้าตาเหมือนที่ LINE เก็บไว้ (เอาแต่ field ที่สคริปต์เทียบ)"""
    return {
        "richMenuId": menu_id,
        "name": name,
        "chatBarText": rm.CHAT_BAR_TEXT,
        "size": {"width": rm.MENU_WIDTH, "height": rm.MENU_HEIGHT},
        "areas": [
            {
                "bounds": rm.cell_bounds(index),
                "action": {
                    "type": "postback",
                    "label": label,
                    "data": rm.postback_data(action),
                },
            }
            for index, (label, action) in enumerate(slots)
        ],
    }


@pytest.fixture
def fake_line(monkeypatch):
    """ติดตั้ง LINE ปลอม + แทน ``get_settings`` เพื่อไม่ให้อ่าน .env จริง"""

    def install(menus=None, default_id=None, image=OLD_IMAGE, consult_id=None) -> FakeLine:
        line = FakeLine(menus=menus, default_id=default_id, image=image)
        monkeypatch.setattr(update_rich_menu, "api_client", lambda: line)
        monkeypatch.setattr(
            update_rich_menu,
            "get_settings",
            lambda: SimpleNamespace(rich_menu_consult_id=consult_id),
        )
        return line

    return install


# ── เทียบเมนู (ไม่ต้องมี token) ──────────────────────────────────────────────


def test_differences_names_the_slots_that_changed() -> None:
    text = "\n".join(
        update_rich_menu.differences(menu("richmenu-old", OLD_SLOTS), rm.build_rich_menu())
    )

    assert "ช่องที่ยังขาด: วางแผนการเรียน, วางแผนเกรด" in text
    assert "ช่องที่ต้องเอาออก: กู้ยืม กยศ., ทำอะไรได้บ้าง" in text


def test_differences_of_the_same_menu_is_empty() -> None:
    assert update_rich_menu.differences(rm.build_rich_menu(), rm.build_rich_menu()) == []


def test_differences_catches_a_renamed_menu() -> None:
    renamed = menu("richmenu-x", rm.SLOTS, name="เมนูชื่อเก่า")
    problems = update_rich_menu.differences(renamed, rm.build_rich_menu())

    assert any("ชื่อเมนูไม่ตรง" in line for line in problems)


# ── เส้นทาง "ไม่ต้องทำอะไร" ─────────────────────────────────────────────────


def test_up_to_date_menu_is_left_alone(fake_line) -> None:
    line = fake_line(
        menus=[menu("richmenu-cur", rm.SLOTS)], default_id="richmenu-cur", image=IMAGE
    )

    assert update_rich_menu.main([]) == 0
    assert line.writes == []
    assert line.default_id == "richmenu-cur"


def test_image_only_change_is_treated_as_outdated(fake_line, capsys) -> None:
    """
    ช่อง/ชื่อเหมือนทุกอย่างแต่ภาพคนละไฟล์ — เคสที่เทียบแค่ ``data`` จะพลาด
    และเป็นเคสจริงของการเปลี่ยนแค่ภาพเมนู
    """
    fake_line(menus=[menu("richmenu-cur", rm.SLOTS)], default_id="richmenu-cur")

    assert update_rich_menu.main(["--check"]) == 1
    assert "ภาพไม่ตรง" in capsys.readouterr().out


# ── --check / --dry-run ต้องไม่แตะอะไร ──────────────────────────────────────


def test_check_on_an_old_menu_reports_and_does_not_touch(fake_line, capsys) -> None:
    line = fake_line(menus=[menu("richmenu-old", OLD_SLOTS)], default_id="richmenu-old")

    assert update_rich_menu.main(["--check"]) == 1
    assert line.writes == []
    assert "make rich-menu-update" in capsys.readouterr().out


def test_dry_run_prints_the_plan_without_touching(fake_line, capsys) -> None:
    line = fake_line(menus=[menu("richmenu-old", OLD_SLOTS)], default_id="richmenu-old")

    assert update_rich_menu.main(["--dry-run"]) == 0
    assert line.writes == []
    assert "(dry-run)" in capsys.readouterr().out


def test_check_reports_when_no_default_menu_exists(fake_line, capsys) -> None:
    fake_line(menus=[], default_id=None)

    assert update_rich_menu.main(["--check"]) == 1
    assert "ยังไม่มีเมนู default" in capsys.readouterr().out


# ── อัปเดตจริง ──────────────────────────────────────────────────────────────


def test_outdated_menu_is_replaced_then_the_old_one_is_deleted(fake_line) -> None:
    """
    ลำดับสำคัญมาก: **ตั้ง default ใบใหม่ก่อน แล้วจึงลบใบเก่า** — สลับกันเมื่อไร
    ผู้ใช้จะไม่เหลือเมนูเลยระหว่างสองคำสั่ง
    """
    line = fake_line(menus=[menu("richmenu-old", OLD_SLOTS)], default_id="richmenu-old")

    assert update_rich_menu.main(["--yes"]) == 0

    assert [kind for kind, _ in line.writes] == ["create", "upload", "set_default", "delete"]
    new_id = line.default_id
    assert new_id != "richmenu-old"
    assert line.menus[new_id]["name"] == rm.MENU_NAME
    assert update_rich_menu.slot_data(line.menus[new_id]) == update_rich_menu.slot_data(
        rm.build_rich_menu()
    )
    assert line.images[new_id] == IMAGE, "ต้องอัปโหลดภาพในเครื่องขึ้นไป ไม่ใช่ภาพเก่า"
    assert "richmenu-old" not in line.menus


def test_existing_matching_menu_is_reused_instead_of_created(fake_line) -> None:
    """channel ที่อัปเดตมาหลายรอบมักมีใบที่ตรงอยู่แล้วค้าง — ตั้ง default ให้ ไม่สร้างซ้ำ"""
    line = fake_line(
        menus=[menu("richmenu-old", OLD_SLOTS), menu("richmenu-same", rm.SLOTS)],
        default_id="richmenu-old",
        image=IMAGE,
    )

    assert update_rich_menu.main(["--yes"]) == 0

    assert [kind for kind, _ in line.writes] == ["set_default", "delete"]
    assert line.default_id == "richmenu-same"
    assert "richmenu-old" not in line.menus


def test_force_creates_a_new_menu_even_when_identical(fake_line) -> None:
    line = fake_line(
        menus=[menu("richmenu-cur", rm.SLOTS)], default_id="richmenu-cur", image=IMAGE
    )

    assert update_rich_menu.main(["--yes", "--force"]) == 0
    assert [kind for kind, _ in line.writes] == ["create", "upload", "set_default", "delete"]


def test_keep_old_leaves_the_previous_menu_on_the_channel(fake_line) -> None:
    line = fake_line(menus=[menu("richmenu-old", OLD_SLOTS)], default_id="richmenu-old")

    assert update_rich_menu.main(["--yes", "--keep-old"]) == 0
    assert "richmenu-old" in line.menus


def test_leftover_menus_are_reported_but_kept_without_prune(fake_line, capsys) -> None:
    line = fake_line(
        menus=[menu("richmenu-old", OLD_SLOTS), menu("richmenu-old2", OLD_SLOTS)],
        default_id="richmenu-old",
    )

    assert update_rich_menu.main(["--yes"]) == 0
    assert "richmenu-old2" in line.menus
    assert "--prune" in capsys.readouterr().out


def test_prune_removes_leftovers_but_not_the_consult_menu(fake_line) -> None:
    line = fake_line(
        menus=[
            menu("richmenu-old", OLD_SLOTS),
            menu("richmenu-old2", OLD_SLOTS),
            menu(CONSULT_ID, rm.CONSULT_SLOTS, name=rm.CONSULT_MENU_NAME),
        ],
        default_id="richmenu-old",
        consult_id=CONSULT_ID,
    )

    assert update_rich_menu.main(["--yes", "--prune"]) == 0
    assert set(line.menus) == {line.default_id, CONSULT_ID}


# ── ด่านยืนยัน ──────────────────────────────────────────────────────────────


def test_no_terminal_means_no_changes_without_yes(fake_line, monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        update_rich_menu.sys, "stdin", SimpleNamespace(isatty=lambda: False)
    )
    line = fake_line(menus=[menu("richmenu-old", OLD_SLOTS)], default_id="richmenu-old")

    assert update_rich_menu.main([]) == 1
    assert line.writes == []
    assert "--yes" in capsys.readouterr().out