from fastapi import APIRouter, UploadFile, File
from botocore.exceptions import ClientError

from ..database import sqlite_connection
from ..s3_utils import upload_file
from ..utils import gen_uuid4

router = APIRouter(prefix="/art", tags=["art"])


@router.post("/create")
async def create_art(art: UploadFile = File(...), character_uuid4: str = gen_uuid4()):
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            art_uuid4 = gen_uuid4()
            upload_file(art, art_uuid4)
            cur.execute(
                "INSERT INTO art VALUES (:uuid4, :character_uuid4)",
                (art_uuid4, character_uuid4),
            )

            con.commit()
            return {"message": f"Art {art_uuid4} record created successfully"}

    except ClientError as e:
        return {"error": str(e)}
