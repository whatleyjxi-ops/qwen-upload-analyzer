请在当前目录从零创建一个完整可运行项目。

项目名称：qwen-upload-analyzer

技术栈：
1. 前端使用 Vue3 + Vite。
2. 后端使用 Python FastAPI。
3. 前后端分目录管理。
4. 本地开发阶段默认 MOCK_QWEN=true，不真实调用 Qwen。
5. 后续 MOCK_QWEN=false 时调用阿里云 DashScope 的 OpenAI 兼容接口。

项目结构：
qwen-upload-analyzer
├─ backend
│  ├─ app
│  │  ├─ main.py
│  │  ├─ config.py
│  │  ├─ validate.py
│  │  ├─ prompt.py
│  │  └─ qwen_service.py
│  ├─ uploads
│  ├─ requirements.txt
│  └─ .env.example
│
└─ frontend
   ├─ src
   │  ├─ api
   │  │  └─ analyzeApi.js
   │  ├─ components
   │  │  └─ UploadAnalyzer.vue
   │  ├─ App.vue
   │  ├─ main.js
   │  └─ style.css
   ├─ package.json
   └─ vite.config.js

功能要求：
1. GET /health 返回 {"status":"ok"}。
2. GET /api/health 返回 {"status":"ok"}。
3. POST /api/analyze/upload 支持 multipart/form-data。
4. 请求字段：
   - category=image|video|document
   - files=上传文件数组
5. 上传文件保存到 backend/uploads。
6. FastAPI 暴露 /uploads 静态访问。
7. 前端点击 + 后显示菜单：
   - 上传文档，最多 1 个
   - 上传图片，最多 5 个，小于 100MB
   - 上传视频，最多 1 个，小于 500MB
8. 图片最多 5 个，单个小于 100MB。
9. 视频最多 1 个，单个小于 500MB。
10. 文档最多 1 个。
11. 视频只限制文件大小，不限制视频时长。
12. 不做限流。
13. 不做费用统计。
14. 不记录 usage.token。
15. 不传 fps。
16. 不传 max_pixels。
17. 不传 total_pixels。
18. 上传成功后自动调用后端分析。
19. 分析中显示 loading。
20. 分析完成后展示结果。
21. 支持清空结果。
22. UI 风格接近 ChatGPT 上传菜单，简洁、清爽。

Qwen 接入要求：
1. backend/.env.example 包含：
   DASHSCOPE_API_KEY=
   DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   QWEN_MODEL=qwen3.6-plus
   MOCK_QWEN=true
   PUBLIC_FILE_BASE_URL=
2. API Key 只能在后端 .env 读取，前端不能出现 API Key。
3. MOCK_QWEN=true 时不真实调用 Qwen，返回模拟结果。
4. MOCK_QWEN=false 时调用真实 Qwen。
5. 图片输入格式：
   {
     "type": "image_url",
     "image_url": { "url": "图片公网URL" }
   }
6. 视频输入格式：
   {
     "type": "video_url",
     "video_url": { "url": "视频公网URL" }
   }
7. 如果 MOCK_QWEN=false 且 PUBLIC_FILE_BASE_URL 为空，要返回明确错误：
   “真实调用 Qwen 时，文件必须通过公网 URL 访问，请配置 PUBLIC_FILE_BASE_URL。”
8. 用户提示词固定写在后端 prompt.py，前端不允许传完整提示词。

本地启动要求：
1. 后端运行在 3000 端口。
2. 前端运行在 5173 端口。
3. Vite 代理 /api 到 http://localhost:3000。
4. README.md 写清楚 Windows CMD 下的启动命令。
5. 添加 .gitignore，忽略：
   - backend/.env
   - backend/.venv
   - frontend/node_modules
   - frontend/dist
   - backend/uploads 中的上传文件，但保留 .gitkeep

请直接生成所有代码文件。生成后请说明如何启动和测试。