from fastapi import APIRouter, Form
from typing import Annotated
from botocore.exceptions import ClientError

from ..database import sqlite_connection
from ..utils import gen_uuid


router = APIRouter(prefix="/character", tags=["character"])


@router.post("/create")
async def create_character(
    character_name: Annotated[str, Form()],
    series_name: Annotated[str, Form()],
    rarity: Annotated[int, Form()],
):
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            cur.execute(
                "INSERT INTO character VALUES (:uuid, :name, :series, :rarity)",
                (gen_uuid(), character_name, series_name, rarity),
            )
            con.commit()

            return {
                "message": f"Character {character_name} record created successfully"
            }
    except ClientError as e:
        return {"error": str(e)}
