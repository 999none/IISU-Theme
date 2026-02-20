from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

THEME_DIR = "/app/iiSU_White_UI"
ZIP_PATH = "/app/iiSU_White_UI.zip"


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/download")
def download_zip():
    return FileResponse(
        ZIP_PATH,
        media_type="application/zip",
        filename="iiSU_White_UI.zip",
    )


@app.get("/api/assets/{filename}")
def get_asset(filename: str):
    safe = os.path.basename(filename)
    path = os.path.join(THEME_DIR, safe)
    if not os.path.isfile(path):
        return {"error": "not found"}
    return FileResponse(path)
