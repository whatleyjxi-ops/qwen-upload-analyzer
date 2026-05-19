请读取本文件，并为当前项目补充阿里云 ECS 部署方案。

当前项目：
- frontend：Vue3 + Vite
- backend：Python FastAPI
- 后端端口：3000
- 前端开发端口：5173
- 生产环境使用 Nginx 托管前端 dist
- Nginx 反向代理 /api 到 FastAPI
- Nginx 暴露 /uploads 静态目录
- 服务器系统：Alibaba Cloud Linux 4
- ECS 配置：2核 4GB，40GB系统盘

请新增以下文件：

1. DEPLOY.md
要求详细写清楚阿里云 ECS 部署步骤，包括：
- 安装 Git
- 安装 Python3 / pip
- 安装 Node.js / npm
- 安装 Nginx
- 拉取 GitHub 仓库
- 安装后端依赖
- 配置 backend/.env
- 前端 npm install
- 前端 npm run build
- 配置 Nginx
- 配置 systemd 后端服务
- 启动服务
- 查看日志
- 验证接口
- 验证上传
- MOCK_QWEN=true 测试
- MOCK_QWEN=false 真实 Qwen 测试

2. deploy/nginx/qwen-upload-analyzer.conf
要求：
- listen 80
- server_name 使用 _ 或示例域名
- root 指向 /opt/qwen-upload-analyzer/frontend/dist
- /api/ 代理到 http://127.0.0.1:3000/api/
- /health 代理到 http://127.0.0.1:3000/health
- /uploads/ 映射到 /opt/qwen-upload-analyzer/backend/uploads/
- 支持较大上传文件，client_max_body_size 600m
- 加上必要的 proxy headers

3. deploy/systemd/qwen-upload-analyzer.service
要求：
- WorkingDirectory=/opt/qwen-upload-analyzer/backend
- ExecStart 使用 python3 -m uvicorn app.main:app --host 127.0.0.1 --port 3000
- Restart=always
- EnvironmentFile=/opt/qwen-upload-analyzer/backend/.env

4. backend/.env.production.example
内容包括：
DASHSCOPE_API_KEY=
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3.6-plus
MOCK_QWEN=true
PUBLIC_FILE_BASE_URL=http://你的服务器公网IP

注意：
- 不要提交 backend/.env
- 不要提交真实 API Key
- 不要修改现有功能逻辑
- 不要添加限流
- 不要添加费用统计
- 不要添加 token 统计
- 不要限制视频时长
- 视频仍然只限制文件大小

完成后请执行验证：
1. cd frontend && npm.cmd install && npm.cmd run build
2. cd ../backend && python -m pip install -r requirements.txt

如果发现报错，请自动修复。