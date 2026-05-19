from pathlib import Path


PROMPT_VERSION = "v3.2"
PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "video_review_v2_2.md"
PROMPT_SOURCE = "backend/app/prompts/video_review_v2_2.md"
SYSTEM_PROMPT = PROMPT_FILE.read_text(encoding="utf-8")


def build_user_instruction(category: str) -> str:
    if category == "video":
        return (
            "请严格按照后端内置《公众人物高相似风险审核与微调指导框架 V3.2》审核本视频。"
            "只输出存在问题的秒级时间段。"
            "重点判断是否存在公众人物高相似风险、内容合规问题和技术质量问题。"
            "公众人物高相似风险必须输出相似度、命中硬特征、画面描述和人工复核提示。"
            "视频禁止输出微调建议，禁止输出总结和解释。"
        )

    if category == "image":
        return (
            "请严格按照后端内置《公众人物高相似风险审核与微调指导框架 V3.2》审核图片。"
            "重点判断是否存在公众人物高相似风险、内容合规问题和技术质量问题。"
            "如图片触发公众人物高相似风险，必须输出骨相层和五官层微调建议。"
            "微调建议禁止涉及光影、妆造、发型、表情、提示词、后期软件。"
            "只输出存在问题的图片；无问题时输出：✅ 全流程审核通过，无需标注。"
        )

    if category == "document":
        return (
            "当前上传的是文档。请参考后端内置审核标准分析文档中可能涉及的内容合规风险。"
            "如果文档内容不可直接读取，请说明限制，不要编造内容。"
        )

    return "请根据后端内置审核标准分析用户上传内容。"