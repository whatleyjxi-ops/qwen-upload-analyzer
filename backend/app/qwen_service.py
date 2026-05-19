from pathlib import Path

from fastapi import HTTPException
from openai import OpenAI

from app.config import Settings
from app.prompt import SYSTEM_PROMPT, USER_PROMPT
from app.validate import UploadCategory


PUBLIC_URL_REQUIRED_MESSAGE = "真实调用 Qwen 时，文件必须通过公网 URL 访问，请配置 PUBLIC_FILE_BASE_URL。"


async def analyze_files(
    *,
    category: UploadCategory,
    saved_files: list[Path],
    settings: Settings,
) -> dict:
    if settings.mock_qwen:
        return _mock_result(category, saved_files)

    if not settings.public_file_base_url:
        raise HTTPException(status_code=400, detail=PUBLIC_URL_REQUIRED_MESSAGE)
    if not settings.dashscope_api_key:
        raise HTTPException(status_code=500, detail="请在后端 .env 中配置 DASHSCOPE_API_KEY。")

    messages = _build_messages(category, saved_files, settings.public_file_base_url)
    client = OpenAI(
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
    )
    response = client.chat.completions.create(
        model=settings.qwen_model,
        messages=messages,
    )
    content = response.choices[0].message.content or ""
    return {
        "mode": "real",
        "category": category.value,
        "file_count": len(saved_files),
        "result": content,
    }


def _mock_result(category: UploadCategory, saved_files: list[Path]) -> dict:
    names = [path.name for path in saved_files]
    return {
        "mode": "mock",
        "category": category.value,
        "file_count": len(saved_files),
        "files": names,
        "result": (
            "这是 MOCK_QWEN=true 下的模拟分析结果。\n\n"
            f"已接收 {len(saved_files)} 个{_category_label(category)}文件：{', '.join(names)}。\n"
            "内容概览：文件已成功上传并保存到后端 uploads 目录。\n"
            "关键发现：本地开发模式不会调用 DashScope/Qwen。\n"
            "建议的下一步：配置 PUBLIC_FILE_BASE_URL 和 DASHSCOPE_API_KEY 后可关闭 MOCK_QWEN 进行真实分析。"
        ),
    }


def _build_messages(
    category: UploadCategory,
    saved_files: list[Path],
    public_file_base_url: str,
) -> list[dict]:
    base_url = public_file_base_url.rstrip("/")
    content: list[dict] = [{"type": "text", "text": USER_PROMPT}]

    for path in saved_files:
        url = f"{base_url}/uploads/{path.name}"
        if category == UploadCategory.image:
            content.append({"type": "image_url", "image_url": {"url": url}})
        elif category == UploadCategory.video:
            content.append({"type": "video_url", "video_url": {"url": url}})
        else:
            content.append({"type": "text", "text": f"文档文件 URL：{url}"})

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": content},
    ]


def _category_label(category: UploadCategory) -> str:
    labels = {
        UploadCategory.image: "图片",
        UploadCategory.video: "视频",
        UploadCategory.document: "文档",
    }
    return labels[category]
