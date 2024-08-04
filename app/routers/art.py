from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from PIL import Image
import io
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


@router.put("/update/{art_uuid4}")
async def update_art(art_uuid4: str, art: UploadFile = File(...)):
    try:
        # Validate dimensions
        image = Image.open(io.BytesIO(await art.read()))
        if image.size != (375, 525):
            raise HTTPException(status_code=400, detail="Image must be 375x525 pixels")

        # Reset file pointer
        await art.seek(0)

        # Overwrite S3 file
        upload_file(art, art_uuid4)

        return {"message": f"Art {art_uuid4} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
