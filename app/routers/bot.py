from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from PIL import Image
from datetime import datetime
import base64
import io

from ..database import sqlite_connection
from ..s3_utils import download_file
from ..artist import draw_text_on_image, combine_images
from ..utils import gen_uuid

router = APIRouter(prefix="/bot", tags=["bot"])


class RollResponse(BaseModel):
    image: str
    art_uuids: List[str]


class ClaimRequest(BaseModel):
    user_id: str
    art_uuid: str


class CardInfo(BaseModel):
    uuid: str
    character_name: str
    series: str
    rarity: int
    claim_time: datetime
    custom_code: Optional[str]


class CollectionResponse(BaseModel):
    cards: List[CardInfo]
    total_cards: int


@router.get("/commands/roll", response_model=RollResponse)
async def roll_command():
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            cur.execute(
                """
                SELECT character.uuid, character.name, character.series, character.rarity, art.uuid AS art_uuid
                FROM character
                JOIN art ON character.uuid = art.character_uuid
                ORDER BY RANDOM()
                LIMIT 3
                """
            )
            characters = cur.fetchall()

            if not characters:
                raise HTTPException(status_code=404, detail="No characters found")

            processed_images = []
            art_uuids = []
            for character in characters:
                character_uuid, character_name, series_name, rarity, art_uuid = (
                    character
                )
                image_data = download_file(art_uuid)

                if isinstance(image_data, dict) and "error" in image_data:
                    print(
                        f"Error fetching image for art UUID {art_uuid}: {image_data['error']}"
                    )
                    continue

                image = Image.open(io.BytesIO(image_data))

                image_with_text = draw_text_on_image(image, character_name, series_name)
                processed_images.append(image_with_text)
                art_uuids.append(art_uuid)

            if not processed_images:
                raise HTTPException(
                    status_code=404, detail="No images found for characters"
                )

            combined_image_bytes = combine_images(processed_images)

            img_str = base64.b64encode(combined_image_bytes).decode()

            return JSONResponse(content={"image": img_str, "art_uuids": art_uuids})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/commands/roll/claim")
async def claim_character(claim: ClaimRequest):
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            cur.execute(
                """
                SELECT art.uuid, character.uuid, character.series
                FROM art
                JOIN character ON art.character_uuid = character.uuid
                WHERE art.uuid = ?
            """,
                (claim.art_uuid,),
            )
            art_info = cur.fetchone()

            if not art_info:
                raise HTTPException(status_code=404, detail="Art not found")

            art_uuid, character_uuid, series_uuid = art_info

            # Get a random border
            cur.execute("SELECT uuid FROM border ORDER BY RANDOM() LIMIT 1")
            border_uuid = cur.fetchone()[0]

            # Insert the claim into the cards table
            new_card_uuid = gen_uuid()
            cur.execute(
                """
                INSERT INTO cards (uuid, discord_id, character, series, art, border, claim_time)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """,
                (
                    new_card_uuid,
                    claim.user_id,
                    character_uuid,
                    series_uuid,
                    art_uuid,
                    border_uuid,
                ),
            )

            con.commit()

            return {
                "status": "success",
                "message": "Character claimed successfully",
                "card_uuid": new_card_uuid,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("commands/collection", response_model=CollectionResponse)
async def get_collection(
    user_id: str,
    page: int = Query(1, ge=1),
    items_per_page: int = Query(10, ge=1, le=50),
    sort_by: str = Query(
        "claim_time", regex="^(character_name|series|rarity|claim_time)$"
    ),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
):
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            cur.execute("SELECT COUNT(*) FROM cards WHERE discord_id = ?", (user_id,))
            total_cards = cur.fetchone()[0]

            offset = (page - 1) * items_per_page
            cur.execute(
                f"""
                SELECT cards.uuid, character.name, series.name, character.rarity, cards.claim_time, cards.custom_code
                FROM cards
                JOIN character ON cards.character = character.uuid
                JOIN series ON cards.series = series.uuid
                WHERE cards.discord_id = ?
                ORDER BY {sort_by} {sort_order}
                LIMIT ? OFFSET ?
            """,
                (user_id, items_per_page, offset),
            )

            cards = [
                CardInfo(
                    uuid=row[0],
                    character_name=row[1],
                    series=row[2],
                    rarity=row[3],
                    claim_time=row[4],
                    custom_code=row[5],
                )
                for row in cur.fetchall()
            ]

            return CollectionResponse(cards=cards, total_cards=total_cards)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
