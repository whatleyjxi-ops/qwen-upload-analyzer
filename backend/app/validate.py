from enum import StrEnum
from typing import Iterable

from fastapi import HTTPException, UploadFile


class UploadCategory(StrEnum):
    image = "image"
    video = "video"
    document = "document"


MAX_IMAGE_FILES = 5
MAX_VIDEO_FILES = 1
MAX_DOCUMENT_FILES = 1
MAX_IMAGE_BYTES = 100 * 1024 * 1024
MAX_VIDEO_BYTES = 500 * 1024 * 1024


def validate_uploads(category: UploadCategory, files: Iterable[UploadFile]) -> list[UploadFile]:
    file_list = list(files)
    if not file_list:
        raise HTTPException(status_code=400, detail="请至少上传一个文件。")

    if category == UploadCategory.image:
        _validate_count(file_list, MAX_IMAGE_FILES, "图片最多上传 5 个。")
        _validate_size(file_list, MAX_IMAGE_BYTES, "单个图片必须小于 100MB。")
    elif category == UploadCategory.video:
        _validate_count(file_list, MAX_VIDEO_FILES, "视频最多上传 1 个。")
        _validate_size(file_list, MAX_VIDEO_BYTES, "单个视频必须小于 500MB。")
    elif category == UploadCategory.document:
        _validate_count(file_list, MAX_DOCUMENT_FILES, "文档最多上传 1 个。")

    return file_list


def _validate_count(files: list[UploadFile], max_count: int, message: str) -> None:
    if len(files) > max_count:
        raise HTTPException(status_code=400, detail=message)


def _validate_size(files: list[UploadFile], max_bytes: int, message: str) -> None:
    for file in files:
        size = getattr(file, "size", None)
        if size is not None and size >= max_bytes:
            raise HTTPException(status_code=400, detail=message)
