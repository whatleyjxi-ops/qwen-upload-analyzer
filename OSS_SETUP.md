# OSS_SETUP

本文档说明如何为本项目配置阿里云 OSS，让本地也能真实调用 Qwen 分析图片和视频。

## 创建 Bucket

在阿里云 OSS 控制台创建 Bucket，建议选择距离 DashScope/Qwen 调用区域较近的地域。Bucket 名称需要全局唯一，创建后记录：

- Bucket 名称，例如 `your-qwen-upload-bucket`
- Endpoint，例如 `https://oss-cn-hangzhou.aliyuncs.com`

## 权限建议

推荐 Bucket 设置为私有读写。项目后端负责上传文件，并为每个对象生成临时签名 URL。Qwen 使用签名 URL 读取文件，不需要把 Bucket 设为公共读，也不需要前端持有 OSS AccessKey。

## RAM 用户和 AccessKey

建议创建专用 RAM 用户或角色，并只授予该 Bucket 所需的最小权限，例如上传对象、读取对象和生成签名 URL 所需的访问权限。不要把 AccessKey 写入前端代码，也不要提交真实 `.env`。

## .env 配置项

后端只从 `backend\.env` 读取密钥和 OSS 配置：

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

## STORAGE_MODE=oss 示例

```env
STORAGE_MODE=oss
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET=your-qwen-upload-bucket
OSS_OBJECT_PREFIX=qwen-upload-analyzer
OSS_SIGNED_URL_EXPIRE_SECONDS=3600
```

当 `STORAGE_MODE=oss` 且 OSS 配置完整时，后端会先把上传文件保存到 `backend/uploads`，再上传到 OSS，并生成签名 URL。

## MOCK_QWEN=false 示例

```env
MOCK_QWEN=false
DASHSCOPE_API_KEY=你的 DashScope API Key
STORAGE_MODE=oss
```

真实调用时，图片会按以下格式传给 Qwen：

```json
{ "type": "image_url", "image_url": { "url": "OSS签名URL" } }
```

视频会按以下格式传给 Qwen：

```json
{ "type": "video_url", "video_url": { "url": "OSS签名URL" } }
```

项目不会传 `fps`、`max_pixels`、`total_pixels`。

## 本地真实分析测试步骤

1. 在 OSS 控制台创建私有 Bucket。
2. 创建 RAM 用户或准备可用 AccessKey，并授予 Bucket 读写权限。
3. 复制 `backend\.env.example` 为 `backend\.env`。
4. 填写 DashScope 和 OSS 配置，设置 `MOCK_QWEN=false`、`STORAGE_MODE=oss`。
5. 启动后端：`uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload`。
6. 启动前端：`npm.cmd run dev`。
7. 上传图片或视频。返回结果中的 `files` 会包含 `ossUrl` 或 `signedUrl`，前端调试信息会显示“已使用 OSS 文件地址”。

## 常见错误排查

### OSS 配置缺失

错误：`OSS 配置不完整，请检查 OSS_ACCESS_KEY_ID、OSS_ACCESS_KEY_SECRET、OSS_ENDPOINT、OSS_BUCKET。`

检查 `backend\.env` 是否包含完整 OSS 配置，并重启后端。

### 签名 URL 访问失败

检查 `OSS_ENDPOINT` 和 `OSS_BUCKET` 是否匹配同一地域，确认对象确实上传成功，并确认 `OSS_SIGNED_URL_EXPIRE_SECONDS` 没有设置过短。

### Qwen 无法读取视频

本地 `localhost` 地址无法被 Qwen 服务端访问。请使用 `STORAGE_MODE=oss`，或在 `STORAGE_MODE=local` 时配置公网可访问的 `PUBLIC_FILE_BASE_URL`。

### 文件过大

当前限制：图片单个小于 100MB，视频单个小于 500MB。超过限制会在后端上传校验阶段返回错误。

### AccessDenied

检查 RAM 用户是否有目标 Bucket 的对象上传和读取权限，确认 AccessKey 没有禁用、过期或填错。

### Endpoint 填错

Endpoint 应使用 Bucket 所在地域的 OSS endpoint，例如 `https://oss-cn-hangzhou.aliyuncs.com`。不要把 Bucket 名称重复写进 endpoint。
