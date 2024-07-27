from fastapi import APIRouter, UploadFile, File, Form
from typing import Annotated
from botocore.exceptions import ClientError

from ..database import sqlite_connection
from ..s3_utils import upload_file
from ..utils import gen_uuid

router = APIRouter(prefix="/art", tags=["art"])


@router.post("/create")
async def create_art(art: UploadFile = File(...), character_uuid: str = gen_uuid()):
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            art_uuid = gen_uuid()
            upload_file(art, art_uuid)
            cur.execute(
                "INSERT INTO art VALUES (:uuid, :character_uuid)",
                (art_uuid, character_uuid),
            )

            con.commit()
            return {"message": f"Art {art_uuid} record created successfully"}

    except ClientError as e:
        return {"error": str(e)}
