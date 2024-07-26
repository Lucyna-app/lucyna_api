from fastapi import APIRouter, Form
from typing import Annotated
from botocore.exceptions import ClientError

from ..database import sqlite_connection
from ..utils import gen_uuid


router = APIRouter(prefix="/series", tags=["series"])


@router.post("/create")
async def create_series(series_name: Annotated[str, Form]):
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            # Search if series exists, if not, create one
            cur.execute("SELECT name FROM series WHERE name = ?", (series_name,))
            series = cur.fetchone()
            if not series:
                cur.execute(
                    "INSERT INTO series VALUES (:uuid, :name)",
                    (gen_uuid(), series_name),
                )

            con.commit()
            return {"message": f"Series {series_name} record created successfully"}

    except ClientError as e:
        return {"error": str(e)}
