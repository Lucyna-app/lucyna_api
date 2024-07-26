from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from database import init_db
from s3_utils import upload_file, download_file
from contextlib import asynccontextmanager
from routers import character

import io


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run at API startup
    init_db()
    yield
    # Run at API shutdown


app = FastAPI(lifespan=lifespan)

app.include_router(character.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


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
