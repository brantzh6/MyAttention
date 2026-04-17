# MyAttention

**An AI-driven evolution system for information, knowledge, and decision support.**

[中文文档](docs/README_zh.md)

---

## What is this?

Most information tools help you manage information. MyAttention is being built
as an **AI-driven evolution system**: a system that continuously improves how
it discovers signals, organizes knowledge, evaluates meaning, and supports
important decisions.

Existing LLMs have static, cutoff, and impersonal knowledge. MyAttention aims
to build a continuously growing cognitive system around your domain of interest.
It should not only retrieve. It should judge, synthesize, and evolve.

Important current reading:

- the project vision has not changed
- the implementation path has changed over time
- `Runtime v0` is an enabling substrate, not the final product identity
- the current active capability line is `Source Intelligence V1`

Alignment reference:

- [docs/IKE_VISION_DESIGN_ARCHITECTURE_PATH_ALIGNMENT_2026-04-17.md](docs/IKE_VISION_DESIGN_ARCHITECTURE_PATH_ALIGNMENT_2026-04-17.md)

---

## Layered Brains And Cross-Cutting Layers

### Information Brain

Continuously perceive the world.

Automatically aggregates information from RSS feeds, web monitoring, and APIs.
Sources are graded by authority, and content is ranked by time, topic, and
importance. Information is not just accumulated. It flows as raw material into
the knowledge layer.

### Knowledge Brain

Distill information into structured knowledge.

Performs entity extraction, relation mining, cross-disciplinary association,
and knowledge reasoning on ingested content to build a multi-domain knowledge
graph. The goal is not to store text fragments, but to construct **a cognitive
model of how the world works**.

### Evolution Brain

Self-observe. Self-correct.

Continuously monitors logs and test results, identifies issues, generates
optimization suggestions, and helps the system improve what it should do next.

### World Model

Provide the cross-domain explanatory structure.

The system is not meant to stop at isolated source ranking. It should build a
working model of objects, systems, context, and relations across domains.

### Thinking Tools / Scientific Methodology

Provide the cross-cutting method layer.

Hypothesis formation, comparison, experiment design, error analysis, and method
iteration should remain first-class parts of the system rather than being
forgotten behind local implementation packets.

The three brains are not a flat list. They are layered:

- information brain feeds knowledge formation
- knowledge brain stabilizes reviewed structure
- evolution brain improves what the system should do next
- world model and methodology cut across all three

---

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Feed Aggregation | Yes | Subscribe to RSS, monitor pages, connect APIs, and fetch signals with ranking |
| Knowledge Base | Yes | Upload docs or index pages and build private vector knowledge bases |
| Multi-model Chat | Yes | Chat with web search, deep reasoning, RAG retrieval, and multi-model judgment |
| Memory | Yes | Extract preferences, facts, and decisions from conversations |
| Knowledge Graph | In progress | Entity extraction, relation mining, cross-disciplinary reasoning |
| Evolution Engine | In progress | Monitoring, diagnosis, issue tracking, self-improvement |
| Notifications | Yes | Push important updates to Feishu or DingTalk |

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
# Edit .env at minimum set one supported LLM key such as QWEN_API_KEY

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
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `QDRANT_URL` | Yes | Qdrant endpoint |
| `QWEN_API_KEY` | Yes | Primary LLM API key |
| `ANTHROPIC_API_KEY` | optional | Claude support |
| `OPENAI_API_KEY` | optional | GPT support |
| `FEISHU_APP_ID` / `FEISHU_APP_SECRET` | optional | Feishu app push |
| `FEISHU_WEBHOOK_URL` | optional | Feishu webhook |
| `DINGTALK_WEBHOOK_URL` | optional | DingTalk push |
| `DEBUG` | optional | Development mode |

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

# Run database migrations
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
