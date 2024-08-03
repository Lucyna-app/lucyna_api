from fastapi import APIRouter, Form, HTTPException
from typing import Annotated
from botocore.exceptions import ClientError

from ..database import sqlite_connection
from ..utils import gen_uuid4
from ..s3_utils import delete_file, get_presigned_url


router = APIRouter(prefix="/series", tags=["series"])


@router.post("/create")
async def create_series(series_name: Annotated[str, Form()], series_uuid4=gen_uuid4()):
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            # Search if series exists and return its uuid4
            # If not, create a series and return it's new uuid4
            cur.execute("SELECT name, uuid4 FROM series WHERE name = ?", (series_name,))
            series = cur.fetchone()
            if not series:
                print("here1")
                series_uuid4 = gen_uuid4()
                cur.execute(
                    "INSERT INTO series VALUES (:uuid4, :name)",
                    (series_uuid4, series_name),
                )
                con.commit()
            else:
                series_uuid4 = series[1]

            print("here2")
            return {"message": f"{series_uuid4}"}

    except ClientError as e:
        return {"error": str(e)}


@router.get("/read_all")
async def read_all_series():
    with sqlite_connection() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM series")
        series = cur.fetchall()
        con.close()

        return {"all_series": series}


@router.get("/{series_uuid4}/characters")
async def get_characters_by_series(series_uuid4: str):
    with sqlite_connection() as con:
        cur = con.cursor()
        cur.execute("SELECT name FROM series WHERE uuid4 = ?", (series_uuid4,))
        series = cur.fetchone()
        if not series:
            raise HTTPException(status_code=404, detail="Series not found")

        cur.execute("SELECT * FROM character WHERE series_uuid4 = ?", (series_uuid4,))
        characters = cur.fetchall()
    return {"series_name": series[0], "characters": characters}


@router.get("/{series_uuid4}/character/{character_uuid4}")
async def get_character_details(series_uuid4: str, character_uuid4: str):
    with sqlite_connection() as con:
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM character WHERE uuid4 = ? AND series_uuid4 = ?",
            (character_uuid4, series_uuid4),
        )
        character = cur.fetchone()
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        cur.execute(
            "SELECT uuid4 FROM art WHERE character_uuid4 = ?", (character_uuid4,)
        )
        arts = cur.fetchall()
        art_urls = [get_presigned_url(art[0]) for art in arts]
    return {"character": character, "art_urls": art_urls}


@router.put("/{series_uuid4}/character/{character_uuid4}")
async def update_character(
    series_uuid4: str, character_uuid4: str, character_data: dict
):
    with sqlite_connection() as con:
        cur = con.cursor()
        cur.execute(
            "UPDATE character SET name = ?, rarity = ? WHERE uuid4 = ? AND series_uuid4 = ?",
            (
                character_data["name"],
                character_data["rarity"],
                character_uuid4,
                series_uuid4,
            ),
        )
        con.commit()
    return {"message": "Character updated successfully"}


@router.delete("/{series_uuid4}/character/{character_uuid4}")
async def delete_character(series_uuid4: str, character_uuid4: str):
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            # Get associated art records
            cur.execute(
                "SELECT uuid4 FROM art WHERE character_uuid4 = ?", (character_uuid4,)
            )
            art_records = cur.fetchall()

            # Delete art files from S3
            for art in art_records:
                delete_file(art[0])

            # Delete art records
            cur.execute("DELETE FROM art WHERE character_uuid4 = ?", (character_uuid4,))

            # Delete cards associated with the character
            cur.execute(
                "DELETE FROM cards WHERE character_uuid4 = ?", (character_uuid4,)
            )

            # Delete character
            cur.execute(
                "DELETE FROM character WHERE uuid4 = ? AND series_uuid4 = ?",
                (character_uuid4, series_uuid4),
            )

            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Character not found")

            con.commit()

        return {"message": "Character, associated art, and cards deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
