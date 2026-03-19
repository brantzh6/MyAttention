# MyAttention

**构建世界知识，洞察规律，支持决策。**

[English](../README.md)

---

## 这是什么

大多数信息工具帮你管理信息。MyAttention 的目标是更深一层：**从海量互联网信息中，持续提炼结构化的世界知识，尤其是跨学科的深层规律，最终为重要决策提供可信的认知支撑。**

现有的大模型知识是静态的、截止的、无个性的。MyAttention 要做的，是围绕你的关注领域，建立一个持续生长的私有知识体系——它不只是检索，而是理解；不只是回答，而是洞察。

---

## 三个大脑

### 信息大脑

持续感知世界的变化。

从 RSS、网页、API 等多源渠道自动抓取信息，按来源权威性分级，按时间、主题、重要性聚合。信息不只是堆积，而是持续向知识层输送原料。

### 知识大脑

将信息提炼为结构化知识。

对抓取内容进行实体提取、关系抽取、跨学科关联与知识推理，建立覆盖多领域的知识图谱。目标是理解概念之间的内在联系，不是存储文本片段，而是构建**世界运行的认知模型**。

### 进化大脑

系统自我观察、自我修正。

持续监控运行日志与测试结果，自动识别问题、归并重复任务、生成优化建议，让系统在使用中不断变得更可靠、更准确。

---

## 主要功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 信息流聚合 | ✅ | 订阅 RSS / 监控网页 / 接入 API，自动抓取，按重要性排序展示 |
| 知识库管理 | ✅ | 上传文档或索引网页，构建私有向量知识库，支持多库分类管理 |
| 多模型对话 | ✅ | 接入主流 LLM，支持联网搜索、深度思考、RAG 知识检索、多模型投票共识 |
| 用户记忆 | ✅ | 从对话自动提取偏好、事实和决策记录，越用越懂你 |
| 知识图谱 | 🔄 | 实体提取、关系抽取、跨学科推理（开发中） |
| 自我进化 | 🔄 | 日志监控、自动测试、问题追踪与系统自优化（开发中） |
| 消息推送 | ✅ | 飞书 / 钉钉通知，将重要信息推送到工作群 |

---

## 快速开始

### 前置依赖

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Qdrant 1.4+

用 Docker 一键启动基础服务：

```bash
docker-compose up -d postgres redis qdrant
```

### 后端

```bash
cd services/api

python -m venv venv
source venv/bin/activate        # Linux/Mac
# 或 venv\Scripts\activate     # Windows

pip install -r requirements.txt

cp .env.example .env
# 编辑 .env，至少填写一个 LLM API Key

alembic upgrade head

uvicorn main:app --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd services/web

npm install
cp .env.local.example .env.local

npm run dev
```

### 访问

| 地址 | 说明 |
|------|------|
| http://localhost:3000 | Web 界面 |
| http://localhost:8000/docs | API 文档 |

---

## 环境变量

### `services/api/.env`

| 变量 | 必填 | 说明 |
|------|------|------|
| `DATABASE_URL` | ✅ | PostgreSQL 连接串 |
| `REDIS_URL` | ✅ | Redis 连接串 |
| `QDRANT_URL` | ✅ | Qdrant 地址 |
| `QWEN_API_KEY` | ✅ | 阿里云百炼 API Key（LLM 主入口） |
| `ANTHROPIC_API_KEY` | 可选 | Claude 支持 |
| `OPENAI_API_KEY` | 可选 | GPT 支持 |
| `FEISHU_APP_ID` / `FEISHU_APP_SECRET` | 可选 | 飞书应用推送 |
| `FEISHU_WEBHOOK_URL` | 可选 | 飞书 Webhook 推送（二选一） |
| `DINGTALK_WEBHOOK_URL` | 可选 | 钉钉推送 |
| `DEBUG` | 可选 | 开发模式，默认 `true` |

### `services/web/.env.local`

| 变量 | 说明 |
|------|------|
| `NEXT_PUBLIC_API_URL` | 后端地址，默认 `http://localhost:8000` |

---

## 日常维护

```bash
# 查看服务状态
python manage.py status

# 启动 / 停止全部服务
python manage.py start
python manage.py stop

# 数据库迁移（版本更新后执行）
cd services/api && alembic upgrade head

# 查看日志
tail -f services/api/api.log

# 健康检查
curl http://localhost:8000/health
```

---

## Docker 部署

```bash
docker-compose up -d

# 更新后重新构建
docker-compose build api web
docker-compose up -d api web
```

---

## 文档

| 文档 | 说明 |
|------|------|
| [docs/SPEC.md](../docs/SPEC.md) | 系统愿景与核心定义 |
| [docs/PROJECT_MASTER_PLAN.md](../docs/PROJECT_MASTER_PLAN.md) | 项目总纲与研发约束 |
| [docs/FEATURES.md](../docs/FEATURES.md) | 各功能模块详解 |
| [docs/API.md](../docs/API.md) | API 接口参考 |
| [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md) | 生产部署指南 |
| [docs/SECURITY.md](../docs/SECURITY.md) | 安全配置 |

---

## License

MIT
