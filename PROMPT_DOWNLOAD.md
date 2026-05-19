请读取本文件，并为当前项目增加“分析结果下载功能”。

当前项目：
- frontend：Vue3 + Vite
- backend：Python FastAPI
- 已支持上传图片、视频、文档
- 已支持 MOCK_QWEN=true 模拟分析
- 已支持 MOCK_QWEN=false 调用 Qwen
- 不要修改后端核心逻辑
- 不要添加数据库
- 不要添加限流
- 不要添加费用统计
- 不要限制视频时长
- 不要提交 .env

功能目标：
1. 当分析结果返回后，前端结果区域显示下载按钮。
2. 支持下载 Qwen 推理结果为 Markdown 文件。
3. 支持下载 Qwen 推理结果为 TXT 文件。
4. 支持复制 Qwen 推理结果到剪贴板。
5. 如果后端返回的是 JSON 字符串或对象，要能正常格式化展示和下载。
6. 下载文件名包含：
   - qwen-analysis
   - 上传类型 category，例如 image / video / document
   - 当前时间戳
   示例：
   qwen-analysis-video-20260519-135900.md
7. Markdown 文件内容建议包含：
   - 标题：Qwen 分析结果
   - 分析时间
   - 上传类型
   - 文件列表
   - 分析结果正文
   - debugTiming，如果后端返回了该字段
8. TXT 文件内容也要包含：
   - 分析时间
   - 上传类型
   - 文件列表
   - 分析结果正文
9. 如果当前没有分析结果，下载按钮禁用。
10. 下载功能只在前端实现，使用 Blob 和 URL.createObjectURL。
11. 不要把真实 API Key、OSS AccessKey 写入代码。
12. 保持 npm run build 通过。

UI 要求：
1. 在结果卡片右上角增加操作按钮：
   - 复制结果
   - 下载 MD
   - 下载 TXT
2. 按钮风格保持当前页面简洁风格。
3. 复制成功后显示轻量提示，例如“已复制”。
4. 下载成功不需要弹窗，只触发浏览器下载。
5. 如果复制失败，显示错误提示。

请主要修改：
- frontend/src/components/UploadAnalyzer.vue
- frontend/src/style.css
必要时可以修改 frontend/src/api/analyzeApi.js

完成后执行：
cd frontend
npm.cmd install
npm.cmd run build

如果报错，请自动修复直到通过。