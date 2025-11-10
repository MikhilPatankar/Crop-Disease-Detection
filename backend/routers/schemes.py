from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

from .. import schemas
from ..database import get_db

router = APIRouter(
    tags=["Schemes"],
)

@router.get("/schemes", response_model=List[schemas.SchemePage])
async def get_cached_schemes(db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Retrieve cached scheme pages from the database.
    """
    cursor = db.scheme_pages.find({})
    scheme_pages = await cursor.to_list(length=100)
    if not scheme_pages:
        raise HTTPException(status_code=404, detail="No schemes found in cache.")
    return scheme_pages

