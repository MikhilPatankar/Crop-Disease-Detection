import asyncio
from starlette.concurrency import run_in_threadpool

from . import database
from .config import settings
from requests import get as rget
from traceback import format_exc

def getSchemes():
    schemes = {}
    try:
        url = "https://data.vikaspedia.in/api/public/content/page-content?ctx=/schemesall/schemes-for-farmers&lgn=en"
        headers = {
            "accept": 'application/json, text/plain, */*',
            "accept-encoding": 'gzip, deflate, br, zstd',
            "accept-language": 'en-US,en;q=0.9',
            "access-control-allow-origin": '*',
            "cache-control": 'no-cache',
            "origin": 'https://schemes.vikaspedia.in',
            "pragma": 'no-cache',
            "priority": 'u=1, i',
            "referer": 'https://schemes.vikaspedia.in/',
            "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            "sec-ch-ua-mobile": '?0',
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": 'empty',
            "sec-fetch-mode": 'cors',
            "sec-fetch-site": 'same-site',
            "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        }
        
        response = rget(url, headers=headers).json()
        
        pages = response["contentList"]
        schemes["title"] = response["title"]
        schemes["summary"] = response["summery"]
        _schemes = []
        
        for page in pages[::-1]:
            scheme = {}
            scheme["title"] = page["title"]
            scheme["summary"] = page["summery"]
            scheme["url"] = "https://schemes.vikaspedia.in/viewcontent" + page["context_path"]
            scheme["created_at"] = page["create_at"]
            scheme["updated_at"] = page["updated_at"]
            _schemes.append(scheme)
        schemes["schemes"] = _schemes
    except Exception as e:
        print(f"Requet Error: {e}")
        print(f"Trace: {format_exc()}")
    return schemes


async def update_schemes_cache():
    """
    Fetches schemes from the Vikaspedia API and updates the database cache.
    """
    print("Updating schemes cache...")
    if database.db_client is None:
        print("Database client not available, skipping cache update.")
        return
    try:
        
        fetched_data = await run_in_threadpool(getSchemes)
        if not fetched_data or "schemes" not in fetched_data:
            print("Failed to fetch schemes or data is empty.")
            return

        db = database.db_client[settings.MONGO_DB_NAME]
        await db.scheme_pages.delete_many({})
        
        scheme_page_doc = {
            "title": fetched_data["title"],
            "summary": fetched_data["summary"],
            "schemes": fetched_data["schemes"]
        }
        await db.scheme_pages.insert_one(scheme_page_doc)
        
        print("Schemes cache updated successfully.")
    except Exception as e:
        print(f"Error updating schemes cache: {e}")

async def run_scheme_caching_task():
    """
    Runs the scheme caching task every hour.
    """
    while True:
        await update_schemes_cache()
        
        await asyncio.sleep(3600)

