from fastapi import FastAPI, Form, UploadFile, File
from s3_utils import upload_file
from typing import Annotated
from botocore.exceptions import ClientError
from database import sqlite_connection
import s3_utils
import uuid
from api_main import app


def gen_uuid():
    return str(uuid.uuid4())


@app.post("/upload/character")
async def add_character(
    character_name: Annotated[str, Form()],
    series_name: Annotated[str, Form()],
    rarity: Annotated[int, Form()],
    art: UploadFile = File(...),
):
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            # Search if series exist, if not, create one
            cur.execute("SELECT name FROM series WHERE name = ?", (series_name,))
            series = cur.fetchone()
            if not series:
                cur.execute(
                    "INSERT INTO series VALUES (:uuid, :name)",
                    (gen_uuid(), series_name),
                )

            # Create new character
            cur.execute(
                "INSERT INTO character VALUES (:uuid, :name, :series, :rarity)",
                (gen_uuid(), character_name, series_name, rarity),
            )

            # Create new art
            art_uuid = gen_uuid()
            s3_utils.upload_file(art, art_uuid)
            cur.execute(
                "INSERT INTO art VALUES (:uuid, :character, :series)",
                (art_uuid, character_name, series_name),
            )

            con.commit()
            return {"message": "Character added successfully"}

    except ClientError as e:
        return {"error": str(e)}
