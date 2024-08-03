from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import io

from .database import init_db
from .s3_utils import upload_file, download_file
from .routers import base, character, series, art, bot, border


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run at API startup
    init_db()
    yield
    # Run at API shutdown


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(base.router)
app.include_router(character.router)
app.include_router(series.router)
app.include_router(art.router)
app.include_router(bot.router)
app.include_router(border.router)


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
