# 阿里云 ECS 部署指南

本文档用于将 `qwen-upload-analyzer` 部署到阿里云 ECS。

项目约定：

- 前端：Vue 3 + Vite
- 后端：Python FastAPI
- 后端监听：`127.0.0.1:3000`
- 生产环境：Nginx 托管 `frontend/dist`
- Nginx 反向代理 `/api/` 和 `/health` 到 FastAPI
- Nginx 暴露 `/uploads/` 静态上传目录
- 服务器系统：Alibaba Cloud Linux 4
- 推荐部署目录：`/opt/qwen-upload-analyzer`

## 1. 登录服务器

```bash
ssh root@你的服务器公网IP
```

建议先更新系统软件包：

```bash
sudo dnf update -y
```

## 2. 安装 Git

```bash
sudo dnf install -y git
git --version
```

## 3. 安装 Python3 / pip

Alibaba Cloud Linux 4 通常已内置 Python 3。确认版本：

```bash
python3 --version
python3 -m pip --version
```

如果缺少 pip：

```bash
sudo dnf install -y python3 python3-pip
```

## 4. 安装 Node.js / npm

推荐使用 Node.js 20 LTS：

```bash
sudo dnf install -y nodejs npm
node --version
npm --version
```

如果系统仓库版本过旧，可使用 NodeSource：

```bash
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo dnf install -y nodejs
```

## 5. 安装 Nginx

```bash
sudo dnf install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl status nginx
```

同时在阿里云 ECS 安全组中放行：

- TCP `80`
- 如需 SSH：TCP `22`

## 6. 拉取 GitHub 仓库

将下面的仓库地址替换为你的实际 GitHub 仓库地址：

```bash
sudo mkdir -p /opt
cd /opt
sudo git clone https://github.com/你的用户名/qwen-upload-analyzer.git
sudo chown -R root:root /opt/qwen-upload-analyzer
cd /opt/qwen-upload-analyzer
```

后续更新代码可执行：

```bash
cd /opt/qwen-upload-analyzer
sudo git pull
```

## 7. 安装后端依赖

```bash
cd /opt/qwen-upload-analyzer/backend
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

如果希望隔离依赖，也可以使用虚拟环境。使用虚拟环境时，需要同步调整 systemd 的 `ExecStart`：

```bash
cd /opt/qwen-upload-analyzer/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 8. 配置 backend/.env

不要提交真实 `.env` 和 API Key 到 Git 仓库。

```bash
cd /opt/qwen-upload-analyzer/backend
sudo cp .env.production.example .env
sudo vi .env
```

测试环境可先使用：

```env
DASHSCOPE_API_KEY=
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3.6-plus
MOCK_QWEN=true
PUBLIC_FILE_BASE_URL=http://你的服务器公网IP
```

真实调用 Qwen 时改为：

```env
DASHSCOPE_API_KEY=你的真实DashScope API Key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3.6-plus
MOCK_QWEN=false
PUBLIC_FILE_BASE_URL=http://你的服务器公网IP
```

## 9. 安装前端依赖

```bash
cd /opt/qwen-upload-analyzer/frontend
npm install
```

## 10. 构建前端

```bash
cd /opt/qwen-upload-analyzer/frontend
npm run build
```

构建完成后应生成：

```bash
/opt/qwen-upload-analyzer/frontend/dist
```

## 11. 配置 Nginx

复制项目提供的 Nginx 配置：

```bash
sudo cp /opt/qwen-upload-analyzer/deploy/nginx/qwen-upload-analyzer.conf /etc/nginx/conf.d/qwen-upload-analyzer.conf
```

如有域名，将配置里的：

```nginx
server_name _;
```

改成你的域名：

```nginx
server_name example.com;
```

检查配置并重载：

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 12. 配置 systemd 后端服务

复制项目提供的 systemd 配置：

```bash
sudo cp /opt/qwen-upload-analyzer/deploy/systemd/qwen-upload-analyzer.service /etc/systemd/system/qwen-upload-analyzer.service
sudo systemctl daemon-reload
sudo systemctl enable qwen-upload-analyzer
```

## 13. 启动服务

```bash
sudo systemctl start qwen-upload-analyzer
sudo systemctl status qwen-upload-analyzer
```

重启服务：

```bash
sudo systemctl restart qwen-upload-analyzer
```

## 14. 查看日志

后端服务日志：

```bash
sudo journalctl -u qwen-upload-analyzer -f
```

Nginx 访问日志和错误日志：

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 15. 验证接口

验证后端健康检查：

```bash
curl http://127.0.0.1:3000/health
curl http://127.0.0.1:3000/api/health
```

验证 Nginx 代理：

```bash
curl http://你的服务器公网IP/health
curl http://你的服务器公网IP/api/health
```

期望返回：

```json
{"status":"ok"}
```

## 16. 验证上传

准备一个本地测试文件，例如：

```bash
echo "hello qwen" > /tmp/test.txt
```

调用上传分析接口：

```bash
curl -X POST http://你的服务器公网IP/api/analyze/upload \
  -F "category=text" \
  -F "files=@/tmp/test.txt"
```

如果接口返回 `status: ok`，说明上传链路正常。上传后的文件会保存到：

```bash
/opt/qwen-upload-analyzer/backend/uploads
```

也可以通过 Nginx 的 `/uploads/` 路径访问已保存文件。

## 17. MOCK_QWEN=true 测试

首次部署建议先使用 mock 模式，避免依赖真实 API Key：

```bash
cd /opt/qwen-upload-analyzer/backend
sudo vi .env
```

确认：

```env
MOCK_QWEN=true
```

重启服务：

```bash
sudo systemctl restart qwen-upload-analyzer
```

再次调用上传接口，确认服务、上传和前端页面都能正常工作。

## 18. MOCK_QWEN=false 真实 Qwen 测试

确认已配置真实 DashScope API Key：

```env
DASHSCOPE_API_KEY=你的真实DashScope API Key
MOCK_QWEN=false
```

重启服务：

```bash
sudo systemctl restart qwen-upload-analyzer
```

调用上传接口或通过浏览器访问：

```bash
http://你的服务器公网IP
```

上传文件并确认返回真实 Qwen 分析结果。

## 19. 常见问题排查

后端未启动：

```bash
sudo systemctl status qwen-upload-analyzer
sudo journalctl -u qwen-upload-analyzer -n 100
```

Nginx 配置错误：

```bash
sudo nginx -t
```

端口占用：

```bash
sudo ss -lntp | grep 3000
sudo ss -lntp | grep 80
```

上传文件过大：

- Nginx 已配置 `client_max_body_size 600m`
- 后端仍按项目原有逻辑只限制文件大小，不限制视频时长

静态目录权限问题：

```bash
sudo mkdir -p /opt/qwen-upload-analyzer/backend/uploads
sudo chown -R root:root /opt/qwen-upload-analyzer/backend/uploads
```

