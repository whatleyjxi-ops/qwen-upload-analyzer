from pathlib import Path


PROMPT_VERSION = "v2.2"
PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "video_review_v2_2.md"
PROMPT_SOURCE = "backend/app/prompts/video_review_v2_2.md"
SYSTEM_PROMPT = PROMPT_FILE.read_text(encoding="utf-8")


def build_user_instruction(category: str) -> str:
    if category == "video":
        return (
            "请严格按照后端内置《视频AI审核框架 V2.2》审核本视频，"
            "只输出有问题的时间段。"
        )

    if category == "image":
        return (
            "当前上传的是图片，不能编造视频时间戳，只能参考画面审核标准。"
            "请基于后端内置审核框架中适用于画面内容的标准进行审核，"
            "只输出与图片内容相关的审核结果。"
        )

    if category == "document":
        return (
            "当前上传的是文档，不能编造视频内容。"
            "请基于后端内置审核框架中可适用于文本内容的标准进行审核，"
            "如果无法读取文档内容，请明确说明限制，不要虚构内容。"
        )

    return "请根据后端内置审核标准分析用户上传内容，只输出审核结果。"
