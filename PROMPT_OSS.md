请读取本文件，并为当前项目增加“阿里云 OSS 上传模式”，用于本地也能真实调用 Qwen 分析图片和视频。

当前项目：
- frontend：Vue3 + Vite
- backend：Python FastAPI
- 当前已有 MOCK_QWEN=true 模拟分析
- 当前后端上传文件保存到 backend/uploads
- 当前后端调用 Qwen 使用 OpenAI 兼容接口
- 图片输入使用 image_url
- 视频输入使用 video_url
- 不传 fps、max_pixels、total_pixels
- 不做限流
- 不做费用统计
- 不记录 usage.token
- 不限制视频时长
- 视频只限制文件大小

新增目标：
1. 增加 OSS 上传能力。
2. 本地开发时也可以把上传文件同步上传到 OSS。
3. MOCK_QWEN=false 时，Qwen 使用 OSS 签名 URL 分析图片/视频。
4. OSS Bucket 推荐私有读写，后端生成临时签名 URL 给 Qwen 读取。
5. API Key、OSS AccessKey 只能从 backend/.env 读取，不能出现在前端代码里。
6. 不要提交真实 .env。
7. 不要破坏现有 MOCK_QWEN=true 流程。
8. 默认仍然 MOCK_QWEN=true。
9. 只有当 STORAGE_MODE=oss 且 MOCK_QWEN=false 时，才要求 OSS 配置完整。

请修改后端：
1. backend/requirements.txt 增加 oss2。
2. 新增 backend/app/oss_service.py。
3. backend/app/config.py 增加以下配置：
   STORAGE_MODE=local
   OSS_ACCESS_KEY_ID=
   OSS_ACCESS_KEY_SECRET=
   OSS_ENDPOINT=
   OSS_BUCKET=
   OSS_OBJECT_PREFIX=qwen-upload-analyzer
   OSS_SIGNED_URL_EXPIRE_SECONDS=3600
4. backend/.env.example 增加上述 OSS 配置。
5. backend/.env.production.example 也增加上述 OSS 配置。
6. 后端上传接口 /api/analyze/upload 逻辑调整：
   - 先按原逻辑保存文件到 backend/uploads
   - 如果 STORAGE_MODE=local：继续使用本地 URL
   - 如果 STORAGE_MODE=oss：把文件上传到 OSS，然后生成签名 URL
   - MOCK_QWEN=true 时仍然返回 mock，不强制要求 OSS
   - MOCK_QWEN=false 时，必须保证传给 Qwen 的文件 URL 是公网可访问 URL 或 OSS 签名 URL
7. 如果 STORAGE_MODE=oss 但 OSS 配置缺失，返回明确错误：
   “OSS 配置不完整，请检查 OSS_ACCESS_KEY_ID、OSS_ACCESS_KEY_SECRET、OSS_ENDPOINT、OSS_BUCKET。”
8. 如果 MOCK_QWEN=false 且 STORAGE_MODE=local 且 PUBLIC_FILE_BASE_URL 为空，返回明确错误：
   “真实调用 Qwen 时文件必须可公网访问，请配置 PUBLIC_FILE_BASE_URL 或启用 STORAGE_MODE=oss。”
9. 返回结果中保留 files 字段，并增加 ossUrl 或 signedUrl 字段，方便调试。
10. 不要把签名 URL 永久保存到前端状态以外的地方。

请检查并保持 Qwen 调用格式：
图片：
{
  "type": "image_url",
  "image_url": { "url": "OSS签名URL" }
}

视频：
{
  "type": "video_url",
  "video_url": { "url": "OSS签名URL" }
}

不要传：
- fps
- max_pixels
- total_pixels

前端要求：
1. 尽量不改 UI。
2. 上传成功后，如果返回 files 中有 ossUrl 或 signedUrl，可在调试信息里显示“已使用 OSS 文件地址”。
3. 不要在前端出现任何 API Key 或 OSS AccessKey。
4. 不要让前端直传 OSS，当前阶段由后端上传 OSS。

README.md 要补充：
1. 本地 mock 模式如何运行。
2. 本地真实 Qwen + OSS 模式如何配置。
3. .env 示例说明。
4. OSS Bucket 建议设置为私有。
5. 为什么本地 localhost 不能直接给 Qwen 读取视频。
6. 如何切回 MOCK_QWEN=true。

请新增一个文档：
OSS_SETUP.md

OSS_SETUP.md 内容包括：
1. 创建 OSS Bucket 的建议。
2. 推荐 Bucket 私有读写。
3. 创建 RAM 用户或 AccessKey 的注意事项。
4. .env 配置项说明。
5. STORAGE_MODE=oss 示例。
6. MOCK_QWEN=false 示例。
7. 本地真实分析图片/视频的测试步骤。
8. 常见错误排查：
   - OSS 配置缺失
   - 签名 URL 访问失败
   - Qwen 无法读取视频
   - 文件过大
   - AccessDenied
   - Endpoint 填错

完成后执行本地验证：
1. cd backend
2. python -m pip install -r requirements.txt
3. cd ../frontend
4. npm.cmd install
5. npm.cmd run build

如果有报错，请自动修复直到验证通过。