请读取本文件，并对当前项目做“上传分析耗时可观测 + 用户体验优化”。

当前项目：
- frontend：Vue3 + Vite
- backend：Python FastAPI
- 已支持上传图片、视频、文档
- 已支持 MOCK_QWEN=true 模拟分析
- 已支持 MOCK_QWEN=false 真实调用 Qwen
- 云服务器部署时后端端口为 3100，前端端口为 8088
- 不要改动现有核心功能
- 不要添加限流
- 不要添加费用统计
- 不要限制视频时长
- 视频仍然只限制文件大小

优化目标：
1. 后端在 /api/analyze/upload 中增加耗时日志。
2. 记录并打印：
   - 文件保存耗时
   - OSS 上传耗时，如果 STORAGE_MODE=oss
   - Qwen 调用耗时
   - 总耗时
   - 文件数量
   - 文件总大小
   - category
   - MOCK_QWEN 状态
   - STORAGE_MODE
3. 后端返回 JSON 中增加 debugTiming 字段：
   {
     "saveSeconds": 0.123,
     "ossSeconds": 0,
     "qwenSeconds": 1.23,
     "totalSeconds": 1.5
   }
4. 前端结果区域显示耗时信息，例如：
   - 保存耗时
   - 模型分析耗时
   - 总耗时
5. 前端上传时增加阶段提示：
   - 正在上传文件...
   - 正在等待后端保存...
   - 正在分析中...
   - 分析完成
6. 前端 loading 文案不要只显示一个“分析中”，要让用户知道当前阶段。
7. 如果请求超过 10 秒，显示提示：
   “视频文件较大，分析可能需要更久，请不要关闭页面。”
8. 如果请求超过 30 秒，显示提示：
   “仍在分析中，长视频或大文件会消耗更长时间。”
9. 不要把真实 API Key、AccessKey 写入代码。
10. 不要提交 .env。
11. 保持 npm run build 通过。

完成后执行：
cd backend
python -m pip install -r requirements.txt
cd ../frontend
npm.cmd install
npm.cmd run build

如果报错，请自动修复。