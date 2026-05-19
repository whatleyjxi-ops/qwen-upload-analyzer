from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import oss2
from fastapi import HTTPException

from app.config import Settings


OSS_CONFIG_REQUIRED_MESSAGE = "OSS 配置不完整，请检查 OSS_ACCESS_KEY_ID、OSS_ACCESS_KEY_SECRET、OSS_ENDPOINT、OSS_BUCKET。"


@dataclass(frozen=True)
class UploadedFileRef:
    name: str
    path: Path
    local_url: str
    qwen_url: str
    oss_url: str | None = None
    signed_url: str | None = None

    def to_response(self) -> dict:
        payload = {
            "name": self.name,
            "localUrl": self.local_url,
        }
        if self.oss_url:
            payload["ossUrl"] = self.oss_url
        if self.signed_url:
            payload["signedUrl"] = self.signed_url
        return payload


def is_oss_configured(settings: Settings) -> bool:
    return all(
        [
            settings.oss_access_key_id,
            settings.oss_access_key_secret,
            settings.oss_endpoint,
            settings.oss_bucket,
        ]
    )


def require_oss_config(settings: Settings) -> None:
    if not is_oss_configured(settings):
        raise HTTPException(status_code=400, detail=OSS_CONFIG_REQUIRED_MESSAGE)


def upload_file_to_oss(path: Path, settings: Settings) -> UploadedFileRef:
    require_oss_config(settings)
    bucket = _build_bucket(settings)
    object_key = _build_object_key(path, settings)
    bucket.put_object_from_file(object_key, str(path))
    signed_url = bucket.sign_url("GET", object_key, settings.oss_signed_url_expire_seconds)
    return UploadedFileRef(
        name=path.name,
        path=path,
        local_url=f"/uploads/{quote(path.name)}",
        qwen_url=signed_url,
        oss_url=f"oss://{settings.oss_bucket}/{object_key}",
        signed_url=signed_url,
    )


def build_local_file_ref(path: Path, public_file_base_url: str = "") -> UploadedFileRef:
    local_url = f"/uploads/{quote(path.name)}"
    qwen_url = ""
    if public_file_base_url:
        qwen_url = f"{public_file_base_url.rstrip('/')}/uploads/{quote(path.name)}"
    return UploadedFileRef(
        name=path.name,
        path=path,
        local_url=local_url,
        qwen_url=qwen_url,
    )


def _build_bucket(settings: Settings) -> oss2.Bucket:
    auth = oss2.Auth(settings.oss_access_key_id, settings.oss_access_key_secret)
    return oss2.Bucket(auth, settings.oss_endpoint, settings.oss_bucket)


def _build_object_key(path: Path, settings: Settings) -> str:
    prefix = settings.oss_object_prefix.strip("/")
    object_name = quote(path.name)
    return f"{prefix}/{object_name}" if prefix else object_name
