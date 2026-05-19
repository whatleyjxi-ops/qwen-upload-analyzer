from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import Settings, UPLOAD_DIR, get_settings
from app.oss_service import (
    UploadedFileRef,
    build_local_file_ref,
    is_oss_configured,
    require_oss_config,
    upload_file_to_oss,
)
from app.qwen_service import analyze_files
from app.validate import UploadCategory, validate_uploads


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="qwen-upload-analyzer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/health")
async def api_health() -> dict:
    return {"status": "ok"}


@app.post("/api/analyze/upload")
async def analyze_upload(
    category: UploadCategory = Form(...),
    files: list[UploadFile] = File(...),
) -> dict:
    settings = get_settings()
    valid_files = validate_uploads(category, files)
    saved_files = await _save_files(valid_files)
    file_refs = _build_file_refs(saved_files, settings)
    analysis = await analyze_files(
        category=category,
        files=file_refs,
        settings=settings,
    )
    return {
        "status": "ok",
        "analysis": analysis,
    }


async def _save_files(files: list[UploadFile]) -> list[Path]:
    saved: list[Path] = []
    for file in files:
        original_name = Path(file.filename or "upload").name
        target = UPLOAD_DIR / f"{uuid4().hex}_{original_name}"
        with target.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                output.write(chunk)
        saved.append(target)
    return saved


def _build_file_refs(saved_files: list[Path], settings: Settings) -> list[UploadedFileRef]:
    storage_mode = settings.storage_mode.lower()
    if storage_mode == "oss":
        if settings.mock_qwen and not is_oss_configured(settings):
            return [build_local_file_ref(path, settings.public_file_base_url) for path in saved_files]
        require_oss_config(settings)
        return [upload_file_to_oss(path, settings) for path in saved_files]

    return [build_local_file_ref(path, settings.public_file_base_url) for path in saved_files]
