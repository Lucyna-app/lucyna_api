from fastapi import APIRouter, Form, UploadFile, File
from typing import Annotated
from botocore.exceptions import ClientError

from .character import create_character
from .series import create_series
from .art import create_art

router = APIRouter()


@router.post("/create_complete_character")
async def create_complete_character(
    character_name: Annotated[str, Form()],
    series_name: Annotated[str, Form()],
    rarity: Annotated[int, Form()],
    art: UploadFile = File(...),
):
    try:
        await create_series(series_name)
        await create_character(character_name, series_name, rarity)
        await create_art(character_name, series_name, art)
        return {"message": "Full character record created successfully"}
    except ClientError as e:
        return {"error": str(e)}
