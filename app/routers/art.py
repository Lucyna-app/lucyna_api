from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from botocore.exceptions import ClientError

from ..database import sqlite_connection
from ..s3_utils import upload_file
from ..utils import gen_uuid4

router = APIRouter(prefix="/art", tags=["art"])


@router.post("/create")
async def create_art(art: UploadFile = File(...), character_uuid4: str = Form(...)):
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            # Check if the character exists
            cur.execute(
                "SELECT uuid4 FROM character WHERE uuid4 = ?", (character_uuid4,)
            )
            character = cur.fetchone()
            if not character:
                raise HTTPException(status_code=404, detail="Character not found")

            art_uuid4 = gen_uuid4()
            upload_file(art, art_uuid4)
            cur.execute(
                "INSERT INTO art (uuid4, character_uuid4) VALUES (?, ?)",
                (art_uuid4, character_uuid4),
            )

            con.commit()
            return {"message": f"Art {art_uuid4} record created successfully"}

    except ClientError as e:
        return {"error": str(e)}
