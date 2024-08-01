from fastapi import APIRouter, Form
from typing import Annotated
from botocore.exceptions import ClientError

from ..database import sqlite_connection
from ..utils import gen_uuid4


router = APIRouter(prefix="/series", tags=["series"])


@router.post("/create")
async def create_series(series_name: Annotated[str, Form()], series_uuid4=gen_uuid4()):
    try:
        with sqlite_connection() as con:
            cur = con.cursor()

            # Search if series exists and return its uuid4
            # If not, create a series and return it's new uuid4
            cur.execute("SELECT name, uuid4 FROM series WHERE name = ?", (series_name,))
            series = cur.fetchone()
            if not series:
                print("here1")
                series_uuid4 = gen_uuid4()
                cur.execute(
                    "INSERT INTO series VALUES (:uuid4, :name)",
                    (series_uuid4, series_name),
                )
                con.commit()
            else:
                series_uuid4 = series[1]

            print("here2")
            return {"message": f"{series_uuid4}"}

    except ClientError as e:
        return {"error": str(e)}


@router.get("/read_all")
async def read_all_series():
    with sqlite_connection() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM series")
        series = cur.fetchall()
        con.close()

        return {"all_series": series}
