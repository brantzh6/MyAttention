# MyAttention

> 利用 AI 整理世界知识，并为决策提供支持

MyAttention 是一个面向个人的 AI 智能信息助手。它自动聚合你关注的信息源，帮你整理成结构化知识，并通过多模型对话系统随时回答你的问题、辅助你做出更好的决策。

---

## 它能做什么

**订阅和追踪信息**
订阅 RSS、监控网页、接入 API 源，系统自动抓取并按重要性排序，省去手动浏览的时间。

**与你的知识库对话**
将文档、网页、搜索结果存入个人知识库，然后直接用自然语言提问，系统检索相关内容后由 AI 作答，并标注来源。

**多模型智能对话**
接入主流 LLM 提供商，支持普通对话、联网搜索、深度思考，以及多模型同时回答后投票取共识（适合重要决策）。

**记忆你的偏好**
从对话中自动提取你的偏好、事实和决策记录，后续对话中自动带入上下文，越用越懂你。

**推送重要信息**
通过飞书或钉钉机器人，将重要信息、定时简报推送到你的工作群。

---

## 快速开始

### 前置依赖

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Qdrant 1.4+

### 1. 启动基础服务

确保 PostgreSQL、Redis、Qdrant 已在本地运行，或使用 Docker 一键启动：

```bash
docker-compose up -d postgres redis qdrant
```

### 2. 配置后端

```bash
cd services/api

python -m venv venv
source venv/bin/activate        # Linux/Mac
# 或 venv\Scripts\activate     # Windows

pip install -r requirements.txt

cp .env.example .env
# 编辑 .env，至少填写 QWEN_API_KEY（其他 LLM Key 按需填写）

alembic upgrade head

uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. 配置前端

```bash
cd services/web

npm install

cp .env.local.example .env.local
# 默认指向 http://localhost:8000，无需修改即可启动

npm run dev
```

### 4. 访问

- 应用界面：http://localhost:3000
- API 文档：http://localhost:8000/docs

---

## 环境变量说明

### `services/api/.env`

| 变量 | 必填 | 说明 |
|------|------|------|
| `DATABASE_URL` | ✅ | PostgreSQL 连接串 |
| `REDIS_URL` | ✅ | Redis 连接串 |
| `QDRANT_URL` | ✅ | Qdrant 地址 |
| `QWEN_API_KEY` | ✅ | 阿里云百炼 API Key（主要 LLM） |
| `ANTHROPIC_API_KEY` | 可选 | Claude 支持 |
| `OPENAI_API_KEY` | 可选 | GPT 支持 |
| `FEISHU_APP_ID` / `FEISHU_APP_SECRET` | 可选 | 飞书应用模式推送 |
| `FEISHU_WEBHOOK_URL` | 可选 | 飞书 Webhook 推送（二选一） |
| `DINGTALK_WEBHOOK_URL` | 可选 | 钉钉推送 |
| `DEBUG` | 可选 | 开发模式，默认 `true` |

### `services/web/.env.local`

| 变量 | 说明 |
|------|------|
| `NEXT_PUBLIC_API_URL` | 后端 API 地址，默认 `http://localhost:8000` |

---

## 日常维护

### 查看服务状态

```bash
python manage.py status
```

### 启动 / 停止所有服务

```bash
python manage.py start
python manage.py stop
```

### 数据库迁移

新版本发布后若有数据库变更：

```bash
cd services/api
alembic upgrade head
```

### 日志

```bash
# API 日志
tail -f services/api/api.log

# Docker 模式
docker-compose logs -f api
docker-compose logs -f web
```

### 健康检查

```bash
curl http://localhost:8000/health
# 返回 {"status": "healthy"}
```

---

## Docker 部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 更新代码后重新构建
docker-compose build api web
docker-compose up -d api web

# 停止
docker-compose down
```

---

## 更多文档

| 文档 | 说明 |
|------|------|
| [docs/FEATURES.md](docs/FEATURES.md) | 各功能详细说明 |
| [docs/API.md](docs/API.md) | API 接口参考 |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | 生产环境部署（Nginx、SSL、备份等） |
| [docs/SECURITY.md](docs/SECURITY.md) | 安全配置建议 |

---

## License

MIT
