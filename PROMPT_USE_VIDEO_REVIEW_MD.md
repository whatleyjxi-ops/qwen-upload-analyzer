请读取本文件，并修复当前项目的后端预设提示词加载方式。

目标：
不要再把长提示词直接写死在 Python 字符串里。
请让 backend/app/prompt.py 从 markdown 文件读取完整提示词。

当前完整提示词文件路径：
backend/app/prompts/video_review_v2_2.md

要求：
1. 新增或保留 backend/app/prompts/video_review_v2_2.md。
2. backend/app/prompt.py 中读取该 markdown 文件作为 SYSTEM_PROMPT。
3. prompt.py 中设置：
   PROMPT_VERSION = "v2.2"
4. prompt.py 中提供：
   build_user_instruction(category: str) -> str
5. video 类型必须返回类似：
   “请严格按照后端内置《视频AI审核框架 V2.2》审核本视频，只输出有问题的时间段。”
6. image 类型必须明确：
   当前上传的是图片，不能编造视频时间戳，只能参考画面审核标准。
7. document 类型必须明确：
   当前上传的是文档，不能编造视频内容。
8. backend/app/qwen_service.py 调用 Qwen 时必须使用：
   system role: SYSTEM_PROMPT
   user role: build_user_instruction(category) + image_url/video_url/text
9. 不要把完整提示词返回给前端。
10. 返回结果中保留：
   promptApplied: true
   promptSource: "backend/app/prompts/video_review_v2_2.md"
   promptVersion: "v2.2"
11. 前端只显示：
   已应用后端预设提示词
   promptVersion: v2.2
12. 不要改 .env。
13. 不要写入任何 API Key。
14. 不要添加限流、费用统计、token 统计。
15. 不要限制视频时长。
16. 保持 npm run build 通过。

建议 prompt.py 结构：

from pathlib import Path

PROMPT_VERSION = "v2.2"
PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "video_review_v2_2.md"
SYSTEM_PROMPT = PROMPT_FILE.read_text(encoding="utf-8")

def build_user_instruction(category: str) -> str:
    ...

完成后执行：
cd backend
python -m pip install -r requirements.txt
cd ../frontend
npm.cmd install
npm.cmd run build

如果报错，请自动修复。