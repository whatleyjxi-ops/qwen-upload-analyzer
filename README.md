# qwen-upload-analyzer

Vue3 + Vite 前端与 FastAPI 后端分目录项目。默认 `MOCK_QWEN=true`，本地开发不会真实调用 Qwen；关闭 mock 后通过阿里云 DashScope OpenAI 兼容接口调用 Qwen。

## 目录

```text
backend   FastAPI 服务，端口 3000
frontend  Vue3 + Vite 应用，端口 5173
```

## 本地 mock 模式

mock 是默认模式，适合只验证上传、前端交互和后端保存文件流程。

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

确认 `backend\.env` 中保持：

```env
MOCK_QWEN=true
STORAGE_MODE=local
```

启动前端：

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

## 本地真实 Qwen + OSS 模式

本地真实调用图片或视频分析时，Qwen 需要读取上传文件。`localhost` 只在你自己的电脑可访问，DashScope/Qwen 服务端无法直接访问 `http://localhost:3000/uploads/...`，因此本地真实分析建议启用 OSS，由后端上传文件并生成临时签名 URL 给 Qwen。

编辑 `backend\.env`：

```env
DASHSCOPE_API_KEY=你的 DashScope API Key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3.6-plus
MOCK_QWEN=false
PUBLIC_FILE_BASE_URL=

STORAGE_MODE=oss
OSS_ACCESS_KEY_ID=你的 RAM AccessKey ID
OSS_ACCESS_KEY_SECRET=你的 RAM AccessKey Secret
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET=你的 Bucket 名称
OSS_OBJECT_PREFIX=qwen-upload-analyzer
OSS_SIGNED_URL_EXPIRE_SECONDS=3600
```

OSS Bucket 建议设置为私有读写。后端会用 AccessKey 上传文件，并只把临时签名 URL 传给 Qwen 读取，不需要让前端直传 OSS。

## .env 示例说明

`backend\.env.example` 和 `backend\.env.production.example` 只提供占位配置，不要提交真实 `.env`。

关键配置：

- `MOCK_QWEN=true`：返回模拟分析结果，不调用 DashScope/Qwen。
- `MOCK_QWEN=false`：真实调用 Qwen，需要 `DASHSCOPE_API_KEY`。
- `STORAGE_MODE=local`：使用本地 `/uploads` 文件地址；真实调用时必须配置公网可访问的 `PUBLIC_FILE_BASE_URL`。
- `STORAGE_MODE=oss`：后端同步上传 OSS，并生成临时签名 URL 给 Qwen。
- `OSS_SIGNED_URL_EXPIRE_SECONDS`：签名 URL 有效期，默认 3600 秒。

## 切回 mock

把 `backend\.env` 改回：

```env
MOCK_QWEN=true
STORAGE_MODE=local
```

重启后端即可。此时不会强制要求 OSS 配置完整。

## 健康检查

```cmd
curl http://localhost:3000/health
curl http://localhost:3000/api/health
```

## 构建验证

```cmd
cd backend
python -m pip install -r requirements.txt
cd ../frontend
npm.cmd install
npm.cmd run build
```
