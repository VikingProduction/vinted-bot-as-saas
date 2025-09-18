# backend/app/tasks/scraper.py

import asyncio
from backend.app.scraping import run_filters
from backend.app.utils.event_bus import publish_event

POLL_INTERVAL = 1  # en secondes

async def run_continuous_scraping():
    while True:
        results = run_filters()  # logique existante
        for item in results.new_items:
            await publish_event("vinted.new_item", item.dict())
        await asyncio.sleep(POLL_INTERVAL)
