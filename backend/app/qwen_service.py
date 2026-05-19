from fastapi import HTTPException
from openai import OpenAI

from app.config import Settings
from app.oss_service import UploadedFileRef
from app.prompt import PROMPT_SOURCE, PROMPT_VERSION, SYSTEM_PROMPT, build_user_instruction
from app.validate import UploadCategory


PUBLIC_URL_REQUIRED_MESSAGE = "真实调用 Qwen 时文件必须可公网访问，请配置 PUBLIC_FILE_BASE_URL 或启用 STORAGE_MODE=oss。"


async def analyze_files(
    *,
    category: UploadCategory,
    files: list[UploadedFileRef],
    settings: Settings,
) -> dict:
    if settings.mock_qwen:
        return _mock_result(category, files)

    if settings.storage_mode.lower() == "local" and not settings.public_file_base_url:
        raise HTTPException(status_code=400, detail=PUBLIC_URL_REQUIRED_MESSAGE)
    if not settings.dashscope_api_key:
        raise HTTPException(status_code=500, detail="请在后端 .env 中配置 DASHSCOPE_API_KEY。")

    messages = _build_messages(category, files)

    client = OpenAI(
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
    )

    response = client.chat.completions.create(
        model=settings.qwen_model,
        messages=messages,
        extra_body={
            "enable_search": True,
            "search_options": {
                "forced_search": True
            },
        },
    )

    content = response.choices[0].message.content or ""

    return {
        "mode": "real",
        "category": category.value,
        "file_count": len(files),
        "files": [file.to_response() for file in files],
        "result": content,
        "promptApplied": True,
        "promptSource": PROMPT_SOURCE,
        "promptVersion": PROMPT_VERSION,
        "webSearchEnabled": True,
        "webSearchForced": True,
    }


def _mock_result(category: UploadCategory, files: list[UploadedFileRef]) -> dict:
    names = [file.name for file in files]
    return {
        "mode": "mock",
        "category": category.value,
        "file_count": len(files),
        "files": [file.to_response() for file in files],
        "promptApplied": True,
        "promptSource": PROMPT_SOURCE,
        "promptVersion": PROMPT_VERSION,
        "webSearchEnabled": False,
        "webSearchForced": False,
        "result": (
            "这是 MOCK_QWEN=true 下的模拟分析结果。\n\n"
            f"已接收 {len(files)} 个{_category_label(category)}文件：{', '.join(names)}。\n"
            "内容概览：文件已成功上传并保存到后端 uploads 目录。\n"
            "关键发现：本地开发模式不会调用 DashScope/Qwen。\n"
            "联网搜索：MOCK 模式下不会启用联网搜索。\n"
            "建议的下一步：配置 PUBLIC_FILE_BASE_URL 或 STORAGE_MODE=oss，并配置 DASHSCOPE_API_KEY 后可关闭 MOCK_QWEN 进行真实分析。"
        ),
    }


def _build_messages(
    category: UploadCategory,
    files: list[UploadedFileRef],
) -> list[dict]:
    content: list[dict] = [
        {
            "type": "text",
            "text": build_user_instruction(category.value),
        }
    ]

    for file in files:
        url = file.qwen_url
        if not url:
            raise HTTPException(status_code=400, detail=PUBLIC_URL_REQUIRED_MESSAGE)

        if category == UploadCategory.image:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": url,
                    },
                }
            )
        elif category == UploadCategory.video:
            content.append(
                {
                    "type": "video_url",
                    "video_url": {
                        "url": url,
                    },
                }
            )
        else:
            content.append(
                {
                    "type": "text",
                    "text": f"文档文件 URL：{url}",
                }
            )

    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": content,
        },
    ]


def _category_label(category: UploadCategory) -> str:
    labels = {
        UploadCategory.image: "图片",
        UploadCategory.video: "视频",
        UploadCategory.document: "文档",
    }
    return labels[category]