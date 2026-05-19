SYSTEM_PROMPT = "你是一个专业的文件内容分析助手。请根据用户上传的文件给出简洁、准确、可执行的分析。"

USER_PROMPT = """
请分析上传文件的主要内容，并按以下结构返回：
1. 内容概览
2. 关键发现
3. 可能的风险或注意事项
4. 建议的下一步

不要输出 token 用量、费用统计、fps、max_pixels 或 total_pixels。
""".strip()
