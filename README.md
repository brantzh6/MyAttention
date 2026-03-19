# MyAttention

> 利用 AI 整理世界知识，并为决策提供支持

MyAttention 是一个 AI 驱动的智能决策支持系统，集成了信息流聚合、多模型智能对话、知识库管理和自我进化能力。

---

## 核心功能

| 模块 | 状态 | 说明 |
|------|------|------|
| 信息流 (Feed) | ✅ 完成 | RSS 订阅、网页监控、权威分级、反爬处理 |
| 智能对话 (Chat) | ✅ 完成 | 多模型支持、RAG 检索、多模型投票 |
| 知识管理 (Knowledge) | ✅ 完成 | 多知识库、向量存储、知识图谱 |
| 知识大脑 (Knowledge Brain) | 🔄 开发中 | 实体提取、关系推理 |
| 进化大脑 (Evolution Brain) | 🔄 开发中 | 自动测试、性能监控、策略自优化 |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 14, React 18, TypeScript, Tailwind CSS |
| 后端 | FastAPI, Python 3.11+, asyncio |
| 存储 | PostgreSQL, Qdrant (向量), Redis, LocalObjectStore / MinIO / S3 |
| LLM | Qwen, DeepSeek, GLM, Kimi, Claude, GPT |
| 协议 | REST, A2A, MCP |
| 自动化 | Playwright (UI 测试) |

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端层 (Frontend)                         │
│                   Next.js 14 + React 18 + TypeScript            │
│                         http://localhost:3000                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API 网关层 (Gateway)                      │
│                      FastAPI + Uvicorn                          │
│                         http://localhost:8000                   │
└───────────────────────────────┬─────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐    ┌───────────────────┐    ┌───────────────────┐
│   对话服务     │    │    知识库服务      │    │    进化服务        │
│  Chat Router  │    │   Knowledge Mgr   │    │  Evolution Svc   │
└───────┬───────┘    └─────────┬─────────┘    └─────────┬─────────┘
        └──────────────────────┼────────────────────────┘
                               │
                               ▼
        ┌──────────────────────────────────────────────────────┐
        │                    存储层 (Storage)                    │
        ├───────────────┬──────────────────┬───────────────────┤
        │  PostgreSQL   │      Qdrant      │      Redis        │
        │   关系数据     │     向量存储      │     缓存/队列      │
        └───────────────┴──────────────────┴───────────────────┘
```

---

## 快速开始

### 环境要求

| 软件 | 版本 |
|------|------|
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL | 15+ |
| Qdrant | 1.4+ |
| Redis | 7+ |

### 后端启动

```bash
cd services/api

# 创建虚拟环境
python -m venv venv
source venv/bin/activate      # Linux/Mac
# 或 venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填写 API Key 等配置

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
cd services/web

npm install
cp .env.local.example .env.local
# 编辑 .env.local

npm run dev
```

### Docker 一键启动

```bash
docker-compose up -d
```

启动后访问：
- 前端：http://localhost:3000
- API：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

## 项目结构

```
MyAttention/
├── services/
│   ├── api/                  # FastAPI 后端
│   │   ├── db/               # 数据库模型
│   │   ├── feeds/            # 信息流模块
│   │   ├── knowledge/        # 知识模块
│   │   ├── llm/              # LLM 多模型适配
│   │   ├── memory/           # 记忆引擎
│   │   ├── notifications/    # 通知服务
│   │   ├── pipeline/         # 调度任务
│   │   ├── rag/              # RAG 引擎
│   │   ├── routers/          # API 路由
│   │   └── main.py           # 入口
│   │
│   └── web/                  # Next.js 前端
│       ├── app/              # App Router 页面
│       ├── components/       # UI 组件
│       └── lib/              # 工具库
│
├── migrations/               # 数据库迁移 SQL
├── docs/                     # 详细文档
├── infrastructure/           # Dockerfile & docker-compose
├── scripts/                  # 开发/部署脚本
└── manage.py                 # 服务管理脚本
```

---

## 支持的 LLM 模型

| 模型 | 提供商 | 特点 |
|------|--------|------|
| Qwen Max | 阿里云 | 中文能力强，支持联网搜索 |
| Qwen Plus | 阿里云 | 均衡性能，支持深度思考 |
| DeepSeek V3 | DeepSeek | 性价比高，推理能力强 |
| GLM-5 | 智谱AI | 国产优秀，支持深度思考 |
| MiniMax M2 | MiniMax | 长文本处理 |
| Kimi K2 | 月之暗面 | 128K 长上下文 |

---

## 主要 API

```
# 对话
POST /api/chat

# 知识库
GET  /api/rag/knowledge-bases
POST /api/rag/knowledge-bases
POST /api/rag/knowledge-bases/{id}/documents/file
POST /api/rag/knowledge-bases/{id}/documents/web

# 对话历史
GET  /api/conversations
GET  /api/conversations/{id}/messages

# 记忆
GET  /api/memories
POST /api/memories

# 健康检查
GET  /health
```

完整 API 文档见 [docs/API.md](docs/API.md) 或启动服务后访问 `/docs`。

---

## 通知集成

支持推送到企业协作工具：
- **飞书 Webhook**
- **钉钉 Webhook**

在 `/settings/notifications` 页面配置 Webhook 地址。

---

## 文档

| 文档 | 说明 |
|------|------|
| [docs/SPEC.md](docs/SPEC.md) | 系统规格定义 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 架构设计 |
| [docs/FEATURES.md](docs/FEATURES.md) | 功能详解 |
| [docs/API.md](docs/API.md) | API 参考 |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | 部署指南 |
| [docs/STORAGE_ARCHITECTURE.md](docs/STORAGE_ARCHITECTURE.md) | 存储层架构 |
| [docs/SECURITY.md](docs/SECURITY.md) | 安全配置 |

---

## License

MIT
