from fastapi import APIRouter, Form, HTTPException
from typing import Annotated
from botocore.exceptions import ClientError

from ..database import sqlite_connection
from ..utils import gen_uuid4


router = APIRouter(prefix="/character", tags=["character"])


@router.post("/create")
async def create_character(
    character_name: Annotated[str, Form()],
    series_uuid4: Annotated[str, Form()],
    rarity: Annotated[int, Form()],
    uuid4: str = gen_uuid4(),
):
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            cur.execute(
                "INSERT INTO character VALUES (:uuid4, :name, :series_uuid4, :rarity)",
                (uuid4, character_name, series_uuid4, rarity),
            )
            con.commit()

            return {
                "message": f"Character {character_name} record created successfully"
            }
    except ClientError as e:
        return {"error": str(e)}