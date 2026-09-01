"""CLI scrape กิจกรรม (ใช้ fixture/เว็บจริงตามคำสั่ง)"""
from __future__ import annotations
import argparse, asyncio
import httpx
from app.activities import LIST_URL, fetch_url, parse_list, scrape_activities
from app.config import get_settings
from app.db import Database

async def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--dry-run", action="store_true"); args = p.parse_args()
    async with httpx.AsyncClient(timeout=20, headers={"User-Agent":"RMU Academic Assistant activity scraper; contact admin"}) as client:
        response = await fetch_url(client, LIST_URL)
    rows = parse_list(response.text)
    print({"rows_found": len(rows), "open": sum(r["register_status"] == "open" for r in rows), "upcoming": sum(r["register_status"] == "upcoming" for r in rows), "dry_run": args.dry_run})
    if args.dry_run: return 0
    settings = get_settings(); db = Database(settings.database_url); await db.open()
    try:
        async with httpx.AsyncClient(timeout=20, headers={"User-Agent":"RMU Academic Assistant activity scraper; contact admin"}) as client:
            result = await scrape_activities(db, client, triggered_by="cli")
        print(result)
    finally: await db.close()
    return 0

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
