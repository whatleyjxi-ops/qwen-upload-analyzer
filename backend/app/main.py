from pathlib import Path
import logging
import time
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qwen-upload-analyzer")

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
    total_started = time.perf_counter()
    save_seconds = 0.0
    oss_seconds = 0.0
    qwen_seconds = 0.0
    settings = get_settings()
    valid_files = validate_uploads(category, files)
    file_count = len(valid_files)

    save_started = time.perf_counter()
    saved_files = await _save_files(valid_files)
    save_seconds = time.perf_counter() - save_started
    total_file_size = sum(path.stat().st_size for path in saved_files)

    refs_started = time.perf_counter()
    file_refs = _build_file_refs(saved_files, settings)
    if settings.storage_mode.lower() == "oss":
        oss_seconds = time.perf_counter() - refs_started

    qwen_started = time.perf_counter()
    analysis = await analyze_files(
        category=category,
        files=file_refs,
        settings=settings,
    )
    qwen_seconds = time.perf_counter() - qwen_started
    total_seconds = time.perf_counter() - total_started
    debug_timing = {
        "saveSeconds": round(save_seconds, 3),
        "ossSeconds": round(oss_seconds, 3),
        "qwenSeconds": round(qwen_seconds, 3),
        "totalSeconds": round(total_seconds, 3),
    }

    logger.info(
        "upload analysis timing saveSeconds=%.3f ossSeconds=%.3f qwenSeconds=%.3f "
        "totalSeconds=%.3f fileCount=%s totalFileSize=%s category=%s mockQwen=%s storageMode=%s",
        save_seconds,
        oss_seconds,
        qwen_seconds,
        total_seconds,
        file_count,
        total_file_size,
        category.value,
        settings.mock_qwen,
        settings.storage_mode,
    )

    return {
        "status": "ok",
        "analysis": analysis,
        "debugTiming": debug_timing,
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
