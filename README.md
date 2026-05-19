# qwen-upload-analyzer

Vue3 + Vite 前端与 FastAPI 后端分目录项目。默认 `MOCK_QWEN=true`，本地开发不会真实调用 Qwen；关闭 mock 后通过阿里云 DashScope OpenAI 兼容接口调用 Qwen。

## 目录

```text
backend   FastAPI 服务，端口 3000
frontend  Vue3 + Vite 应用，端口 5173
```

## Windows CMD 启动后端

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

后端健康检查：

```cmd
curl http://localhost:3000/health
curl http://localhost:3000/api/health
```

## Windows CMD 启动前端

```cmd
cd frontend
npm install
npm.cmd run dev
```

前端访问：

```text
http://localhost:5173
```

Vite 已代理 `/api` 到 `http://localhost:3000`。

## 真实 Qwen 调用

编辑 `backend\.env`：

```env
DASHSCOPE_API_KEY=你的 DashScope API Key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3.6-plus
MOCK_QWEN=false
PUBLIC_FILE_BASE_URL=https://你的公网域名
```

当 `MOCK_QWEN=false` 时，上传文件必须能通过公网 URL 访问；否则后端会返回明确错误。

## 构建验证

```cmd
cd frontend
npm.cmd run build
```
