from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from typing import Annotated, List
from botocore.exceptions import ClientError

from ..utils import gen_uuid4
from .character import create_character
from .series import create_series
from .art import create_art
from ..database import sqlite_connection

router = APIRouter()


@router.post("/create_complete_character")
async def create_complete_character(
    character_name: Annotated[str, Form()],
    series_uuid4: Annotated[str, Form()],
    series_name: Annotated[str, Form()],
    rarity: Annotated[int, Form()],
    art: UploadFile = File(...),
):
    try:
        character_uuid4 = gen_uuid4()
        await create_series(series_name)
        await create_character(character_name, series_uuid4, rarity, character_uuid4)
        await create_art(art, character_uuid4)
        return {"message": "Full character record created successfully"}
    except ClientError as e:
        return {"error": str(e)}


# Depracated for now
@router.post("/fetch_three_characters")
async def fetch_three_characters() -> List[dict]:
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            cur.execute(
                "SELECT uuid4, name, series_uuid4 FROM character ORDER BY RANDOM() LIMIT 3"
            )
            results = cur.fetchall()

            if not results:
                raise HTTPException(status_code=404, detail="No characters found")

            characters = [
                {"uuid": uuid4, "name": name, "series_uuid4": series_uuid4}
                for uuid4, name, series_uuid4 in results
            ]

            return characters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
