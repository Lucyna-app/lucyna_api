from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from app.s3_utils import upload_file, download_file
from typing import Union
import io
import uvicorn
import os

app = FastAPI()


@app.get("/")
def read_root():
    return {"access key": os.getenv("LUCYNA_API_S3_ACCESS_KEY_ID")}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    return await upload_file(file)


@app.get("/download/{file_name}")
async def download_image(file_name: str):
    file_content = download_file(file_name)
    if isinstance(file_content, dict) and "error" in file_content:
        return file_content
    return StreamingResponse(io.BytesIO(file_content), media_type="image/png")


if __name__ == "__api_main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
