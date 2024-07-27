from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image
import io

from ..database import sqlite_connection
from ..s3_utils import download_file
from ..artist import draw_text_on_image, combine_images

router = APIRouter(prefix="/bot", tags=["bot"])


@router.get("/commands/roll")
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

            if not processed_images:
                raise HTTPException(
                    status_code=404, detail="No images found for characters"
                )

            combined_image_bytes = combine_images(processed_images)

            return StreamingResponse(
                io.BytesIO(combined_image_bytes), media_type="image/png"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
