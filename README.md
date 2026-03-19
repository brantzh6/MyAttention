# MyAttention

**Build world knowledge. Discover patterns. Support decisions.**

[中文文档](docs/README_zh.md)

---

## What is this?

Most information tools help you manage information. MyAttention goes deeper: **continuously distilling structured world knowledge from the vast internet — especially cross-disciplinary insights — to provide reliable cognitive support for important decisions.**

Existing LLMs have static, cutoff, and impersonal knowledge. MyAttention builds a continuously growing private knowledge system around your domain of interest. It doesn't just retrieve — it understands. It doesn't just answer — it reasons.

---

## Three Brains

### Information Brain

Continuously perceive the world.

Automatically aggregates information from RSS feeds, web monitoring, and APIs. Sources are graded by authority, and content is ranked by time, topic, and importance. Information is not just accumulated — it flows as raw material into the knowledge layer.

### Knowledge Brain

Distill information into structured knowledge.

Performs entity extraction, relation mining, cross-disciplinary association, and knowledge reasoning on ingested content to build a multi-domain knowledge graph. The goal is not to store text fragments, but to construct **a cognitive model of how the world works**.

### Evolution Brain

Self-observe. Self-correct.

Continuously monitors logs and test results, automatically identifies issues, merges duplicate tasks, and generates optimization suggestions — making the system more reliable and accurate over time.

---

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Feed Aggregation | ✅ | Subscribe to RSS / monitor pages / connect APIs, auto-fetch with importance ranking |
| Knowledge Base | ✅ | Upload docs or index web pages, build private vector knowledge bases |
| Multi-model Chat | ✅ | LLM chat with web search, deep thinking, RAG retrieval, and multi-model voting |
| Memory | ✅ | Auto-extracts preferences, facts, and decisions from conversations |
| Knowledge Graph | 🔄 | Entity extraction, relation mining, cross-disciplinary reasoning |
| Evolution Engine | 🔄 | Log monitoring, auto-testing, issue tracking, self-optimization |
| Notifications | ✅ | Push important updates to Feishu / DingTalk groups |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Qdrant 1.4+

Start infrastructure services with Docker:

```bash
docker-compose up -d postgres redis qdrant
```

### Backend

```bash
cd services/api

python -m venv venv
source venv/bin/activate        # Linux/Mac
# or: venv\Scripts\activate    # Windows

pip install -r requirements.txt

cp .env.example .env
# Edit .env — at minimum, set QWEN_API_KEY (or any supported LLM key)

alembic upgrade head

uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd services/web

npm install
cp .env.local.example .env.local

npm run dev
```

### Access

| URL | Description |
|-----|-------------|
| http://localhost:3000 | Web UI |
| http://localhost:8000/docs | API documentation |

---

## Configuration

### `services/api/.env`

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `REDIS_URL` | ✅ | Redis connection string |
| `QDRANT_URL` | ✅ | Qdrant endpoint |
| `QWEN_API_KEY` | ✅ | Primary LLM API key (Alibaba Cloud Bailian) |
| `ANTHROPIC_API_KEY` | optional | Claude support |
| `OPENAI_API_KEY` | optional | GPT support |
| `FEISHU_APP_ID` / `FEISHU_APP_SECRET` | optional | Feishu app push |
| `FEISHU_WEBHOOK_URL` | optional | Feishu Webhook (alternative to app mode) |
| `DINGTALK_WEBHOOK_URL` | optional | DingTalk push |
| `DEBUG` | optional | Development mode, default `true` |

### `services/web/.env.local`

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend URL, default `http://localhost:8000` |

---

## Maintenance

```bash
# Check service status
python manage.py status

# Start / stop all services
python manage.py start
python manage.py stop

# Run database migrations (after version updates)
cd services/api && alembic upgrade head

# View logs
tail -f services/api/api.log

# Health check
curl http://localhost:8000/health
```

---

## Docker Deployment

```bash
# Start all services
docker-compose up -d

# Rebuild after code updates
docker-compose build api web
docker-compose up -d api web
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/SPEC.md](docs/SPEC.md) | System vision and core definitions |
| [docs/PROJECT_MASTER_PLAN.md](docs/PROJECT_MASTER_PLAN.md) | Project master plan and engineering constraints |
| [docs/FEATURES.md](docs/FEATURES.md) | Detailed feature documentation |
| [docs/API.md](docs/API.md) | API reference |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Production deployment guide |
| [docs/SECURITY.md](docs/SECURITY.md) | Security configuration |

---

## License

MIT
