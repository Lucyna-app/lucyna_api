from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from typing import Annotated, List
from botocore.exceptions import ClientError

from ..utils import gen_uuid4
from .character import create_character
from .series import create_series
from .art import create_art

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
