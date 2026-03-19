# MyAttention 部署文档

## 部署架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        生产环境部署架构                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     │
│    │   Nginx     │────▶│   Frontend  │     │   Backend   │     │
│    │  (反向代理)  │     │   Next.js   │     │   FastAPI   │     │
│    │   :443      │     │   :3000     │     │   :8000     │     │
│    └─────────────┘     └─────────────┘     └─────────────┘     │
│           │                                        │            │
│           └────────────────────────────────────────┘            │
│                               │                                │
│    ┌──────────────────────────┼──────────────────────────┐     │
│    │                          │                          │     │
│    ▼                          ▼                          ▼     │
│ ┌────────────┐      ┌──────────────┐      ┌────────────┐      │
│ │ PostgreSQL │      │    Qdrant    │      │   Redis    │      │
│ │   :5432    │      │    :6333     │      │   :6379    │      │
│ └────────────┘      └──────────────┘      └────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 当前推荐运行模式

当前机器和当前阶段推荐：

- `local-process`

即：

- API：本机 Python 进程
- Web：本机 Node.js 进程
- PostgreSQL：本机进程
- Redis：本机进程
- Qdrant：embedded 优先
- Object Storage：`LocalObjectStore`

详细设计见：

- `docs/DEPLOYMENT_RUN_MODES.md`
- `docs/DEPLOYMENT_AUTOMATION_DESIGN.md`

### 说明：对象存储层

除了 PostgreSQL、Qdrant、Redis 之外，系统的长期部署架构还预留了对象存储层，用于承载不适合直接写入关系库的大对象与原始归档数据：

- 开发阶段：默认使用本地文件系统，通过 `LocalObjectStore` 实现
- 生产/扩展阶段：切换到 `MinIO / S3 / OSS` 等对象存储后端，通过统一对象存储接口接入

对象存储主要用于：

- 原始 RSS / HTML / JSON 抓取结果
- PDF / 图片 / 截图等附件
- 中间处理产物、抓取快照与可重放输入

也就是说，本项目的长期存储层应理解为：

- PostgreSQL：结构化事实、任务、聚合分析
- Redis：缓存、队列缓冲、调度状态
- Qdrant：向量索引与语义检索
- Object Storage：原始对象与大文件归档

---

## 1. 环境要求

### 1.1 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 存储 | 20GB | 50GB+ SSD |

### 1.2 软件要求

| 软件 | 版本 |
|------|------|
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL | 15+ |
| Qdrant | 1.4+ |
| Redis | 7+ |
| Object Storage | Local filesystem (dev) / MinIO / S3 / OSS |
| Docker | 24+ (可选) |
| Docker Compose | 2.20+ (可选) |

---

## 2. 开发环境部署

### 2.1 后端部署

```bash
# 1. 克隆代码
git clone https://github.com/your-repo/myattention.git
cd myattention/services/api

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 API Key 等

# 5. 启动基础服务
# 确保 PostgreSQL、Qdrant、Redis 已运行
# 开发模式默认使用 LocalObjectStore
# 生产模式建议配置 MinIO / S3 / OSS

# 6. 运行数据库迁移
alembic upgrade head

# 7. 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2.2 前端部署

```bash
# 1. 进入前端目录
cd myattention/services/web

# 2. 安装依赖
npm install

# 3. 配置环境变量
cp .env.example .env.local
# 编辑 .env.local

# 4. 开发模式运行
npm run dev

# 5. 或构建生产版本
npm run build
npm start
```

---

## 3. Docker 部署

### 3.1 Docker Compose 配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 数据库
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: myattention
      POSTGRES_USER: myattention
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U myattention"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 向量数据库
  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"
      - "6334:6334"

  # 缓存
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  # 可选对象存储（生产/扩展阶段推荐）
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER:-minio}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-minio123}
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"

  # 后端 API
  api:
    build:
      context: ./services/api
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://myattention:${DB_PASSWORD}@postgres:5432/myattention
      QDRANT_URL: http://qdrant:6333
      REDIS_URL: redis://redis:6379
      OBJECT_STORE_BACKEND: ${OBJECT_STORE_BACKEND:-local}
      OBJECT_STORE_ENDPOINT: ${OBJECT_STORE_ENDPOINT:-http://minio:9000}
      QWEN_API_KEY: ${QWEN_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      qdrant:
        condition: service_started
      redis:
        condition: service_started

  # 前端 Web
  web:
    build:
      context: ./services/web
      dockerfile: Dockerfile
    environment:
      API_URL: http://api:8000
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  postgres_data:
  qdrant_data:
  redis_data:
  minio_data:
```

### 3.2 后端 Dockerfile

```dockerfile
# services/api/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.3 前端 Dockerfile

```dockerfile
# services/web/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine AS runner

WORKDIR /app

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["node", "server.js"]
```

### 3.4 Docker 命令

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f api

# 停止服务
docker-compose down

# 清理数据
docker-compose down -v
```

---

## 4. 生产环境部署

### 4.1 服务器准备

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 3. 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. 安装 Nginx
sudo apt install nginx -y
```

### 4.2 Nginx 配置

```nginx
# /etc/nginx/sites-available/myattention
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # 前端
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # SSE 支持
    location /api/chat {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Connection '';
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
    }
}
```

### 4.3 SSL 证书

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 4.4 环境变量配置

```bash
# .env (生产环境)
# 数据库
DATABASE_URL=postgresql+asyncpg://myattention:STRONG_PASSWORD@postgres:5432/myattention
REDIS_URL=redis://redis:6379
QDRANT_URL=http://qdrant:6333

# LLM API Keys
QWEN_API_KEY=sk-your-key
GLM_API_KEY=your-key
KIMI_API_KEY=your-key

# 安全
SECRET_KEY=your-secret-key-here
DEBUG=false

# 通知
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=xxx
```

---

## 5. 进程管理

### 5.1 使用 Systemd

```ini
# /etc/systemd/system/myattention-api.service
[Unit]
Description=MyAttention API Server
After=network.target postgresql.service

[Service]
Type=simple
User=myattention
WorkingDirectory=/opt/myattention/services/api
Environment="PATH=/opt/myattention/services/api/venv/bin"
ExecStart=/opt/myattention/services/api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启用服务
sudo systemctl enable myattention-api
sudo systemctl start myattention-api
```

### 5.2 使用 PM2 (前端)

```bash
# 安装 PM2
npm install -g pm2

# 启动前端
cd services/web
pm2 start npm --name "myattention-web" -- start

# 保存配置
pm2 save
pm2 startup
```

---

## 6. 监控与日志

### 6.1 日志配置

```python
# 日志配置
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/myattention/api.log'),
        logging.StreamHandler()
    ]
)
```

### 6.2 日志轮转

```bash
# /etc/logrotate.d/myattention
/var/log/myattention/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 myattention myattention
}
```

### 6.3 健康检查

```bash
# API 健康检查
curl http://localhost:8000/health

# 响应: {"status": "healthy", "version": "0.1.0"}
```

---

## 7. 备份策略

### 7.1 数据库备份

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup"

# PostgreSQL 备份
pg_dump -U myattention myattention > $BACKUP_DIR/db_$DATE.sql

# Qdrant 备份
curl -X POST http://localhost:6333/collections/kb_default/snapshots

# 保留最近 7 天
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

### 7.2 定时备份

```bash
# crontab -e
0 2 * * * /opt/myattention/scripts/backup.sh
```

---

## 8. 故障排查

### 8.1 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| API 启动失败 | 数据库连接失败 | 检查 DATABASE_URL 配置 |
| 向量检索无结果 | Qdrant 未启动 | 检查 Qdrant 服务状态 |
| LLM 调用失败 | API Key 无效 | 验证 API Key 配置 |
| 前端无法连接后端 | CORS 配置 | 检查 CORS 设置 |

### 8.2 排查命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api

# 检查端口
netstat -tlnp | grep -E '8000|3000|5432|6333|6379'

# 检查磁盘空间
df -h

# 检查内存
free -m
```

---

## 9. 升级指南

### 9.1 滚动升级

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 备份数据
./scripts/backup.sh

# 3. 构建新镜像
docker-compose build

# 4. 停止旧服务
docker-compose stop api web

# 5. 启动新服务
docker-compose up -d api web

# 6. 验证
curl http://localhost:8000/health
```

### 9.2 数据库迁移

```bash
# 运行迁移
docker-compose exec api alembic upgrade head

# 回滚迁移
docker-compose exec api alembic downgrade -1
```

---

## 10. 安全加固

### 10.1 防火墙配置

```bash
# 仅开放必要端口
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 10.2 安全检查清单

- [ ] 更改默认密码
- [ ] 启用 HTTPS
- [ ] 配置防火墙
- [ ] 定期更新系统
- [ ] 启用日志审计
- [ ] 配置备份策略
- [ ] API Key 加密存储
- [ ] 限制数据库远程访问
