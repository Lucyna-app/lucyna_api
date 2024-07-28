from fastapi import APIRouter, Form
from typing import Annotated
from botocore.exceptions import ClientError

from ..database import sqlite_connection
from ..utils import gen_uuid4

router = APIRouter(prefix="/border", tags=["border"])


@router.post("/create")
async def create_border(
    border_name: Annotated[str, Form()],
    border_rarity: Annotated[int, Form()],
    uuid4: str = gen_uuid4(),
):
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            cur.execute(
                "INSERT INTO border VALUES (:uuid4, :name, :rarity)",
                (uuid4, border_name, border_rarity),
            )
            con.commit()

            return {"message": f"Border {border_name} record created successfully"}
    except ClientError as e:
        return {"error": str(e)}
