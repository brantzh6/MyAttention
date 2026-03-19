# 自我进化系统 - 实现文档

## 1. 实现概述

### 1.1 技术栈

| 组件 | 技术 |
|-----|------|
| 编程语言 | Python 3.14 |
| 异步框架 | asyncio |
| HTTP 客户端 | aiohttp |
| 数据库 | PostgreSQL + asyncpg |
| 协议 | REST, A2A, MCP |

### 1.2 文件结构

```
services/api/
├── feeds/
│   ├── anti_crawl.py          # 自动反爬系统
│   ├── ai_brain.py            # AI 决策大脑
│   ├── evolution.py           # 进化引擎
│   ├── metrics.py             # 指标收集器
│   ├── auto_evolution.py      # 自动启动器
│   ├── external_agent.py       # 外部 Agent 集成
│   └── ai_tester.py            # AI 测试代理
│
├── knowledge/
│   └── graph.py               # 知识图谱
│
├── pipeline/
│   └── evolution_scheduler.py # 进化调度器
│
├── routers/
│   ├── evolution.py           # 进化系统 API
│   └── testing.py             # 测试系统 API
│
└── db/
    └── models.py              # 数据模型（已更新）
```

---

## 2. 核心模块实现

### 2.1 反爬处理 (feeds/anti_crawl.py)

#### AntiCrawlDetector 类

```python
class AntiCrawlDetector:
    """自动反爬检测器"""

    BLOCKED_PATTERNS = [
        r"403 Forbidden",
        r"Access Denied",
        r"Cloudflare",
        r"请验证",
    ]

    def detect(self, status_code: int, content: str) -> AntiCrawlStatus:
        """检测反爬状态"""
        # 1. 基于状态码
        if status_code == 403:
            return AntiCrawlStatus.BLOCKED
        elif status_code == 429:
            return AntiCrawlStatus.RATE_LIMITED

        # 2. 基于内容特征
        for pattern in self._blocked_re:
            if pattern.search(content_lower):
                return AntiCrawlStatus.BLOCKED

        return AntiCrawlStatus.OK
```

---

## 3. API 接口

### 3.1 进化系统 API

| 方法 | 路径 | 说明 |
|-----|------|------|
| POST | `/api/evolution/sources/evaluate` | 评估单个信息源 |
| POST | `/api/evolution/sources/evolve-all` | 批量进化所有源 |
| POST | `/api/evolution/trigger` | 手动触发进化 |
| GET | `/api/evolution/status` | 获取系统状态 |
| POST | `/api/evolution/anti-crawl/test` | 测试 URL 反爬情况 |
| POST | `/api/evolution/knowledge/extract` | 从文本提取知识 |
| POST | `/api/evolution/knowledge/search` | 搜索知识图谱 |
| GET | `/api/evolution/knowledge/reason` | 知识推理 |
| GET | `/api/evolution/knowledge/categories` | 获取分类树 |
| POST | `/api/evolution/ai/decide` | AI 决策 |
| POST | `/api/evolution/ai/analyze` | AI 分析问题 |
| POST | `/api/evolution/ai/discover-sources` | AI 发现新源 |
| GET | `/api/evolution/metrics/source/{source_id}` | 获取源指标 |
| GET | `/api/evolution/metrics/knowledge/{kb_id}` | 获取知识库指标 |

### 3.2 测试系统 API

| 方法 | 路径 | 说明 |
|-----|------|------|
| POST | `/api/testing/run` | 运行完整测试套件 |
| GET | `/api/testing/issues` | 获取发现的问题 |
| GET | `/api/testing/history` | 获取测试历史 |
| GET | `/api/testing/health` | 健康检查 |

---

## 4. 完整 API 列表

```
# 进化系统
POST   /api/evolution/sources/evaluate      评估信息源
POST   /api/evolution/sources/evolve-all    批量进化
POST   /api/evolution/trigger               手动触发
GET    /api/evolution/status                系统状态
POST   /api/evolution/anti-crawl/test       反爬测试
POST   /api/evolution/knowledge/extract     知识提取
POST   /api/evolution/knowledge/search     知识搜索
GET    /api/evolution/knowledge/reason      知识推理
GET    /api/evolution/knowledge/categories 分类树
POST   /api/evolution/ai/decide             AI 决策
POST   /api/evolution/ai/analyze            AI 分析
POST   /api/evolution/ai/discover-sources   AI 发现源
GET    /api/evolution/metrics/source/{id}  源指标
GET    /api/evolution/metrics/knowledge/{id} 知识指标

# 测试系统
POST   /api/testing/run                    运行测试
GET    /api/testing/issues                 问题列表
GET    /api/testing/history                测试历史
GET    /api/testing/health                 健康检查
```

---

## 5. 数据库迁移

### 执行迁移

```bash
docker exec -i myattention-postgres psql -U myattention -d myattention \
    -f migrations/004_evolution_system.sql
```

### 创建的表

- `source_metrics` - 信息源效果指标
- `source_candidates` - 潜在信息源
- `knowledge_metrics` - 知识质量指标
- `knowledge_entities` - 知识实体
- `knowledge_relations` - 知识关系
- `knowledge_categories` - 知识分类

### 新增字段

- `sources.evolution_score` - 进化评分
- `sources.last_evaluated_at` - 最后评估时间

---

## 6. 配置说明

### 环境变量

```bash
# .env 文件

# 外部 AI Agent (可选)
AGENT_ENDPOINT=http://localhost:8080
AGENT_API_KEY=your-api-key
AGENT_PROTOCOL=a2a  # rest | a2a | mcp

# 进化系统配置
EVOLUTION_INTERVAL=3600      # 进化周期(秒)
CHECK_INTERVAL=1800         # 检查周期(秒)
```

---

## 7. 部署验证

```bash
# 测试 API 可用性
curl http://localhost:8000/api/evolution/status

# 触发进化
curl -X POST http://localhost:8000/api/evolution/trigger

# 运行测试
curl -X POST http://localhost:8000/api/testing/run

# 健康检查
curl http://localhost:8000/api/testing/health
```

---

## 8. 测试结果

### API 测试 (2026-03-13)

| 测试 | 状态 |
|-----|------|
| 基础对话 | ✅ 通过 |
| RAG 对话 | ✅ 通过 |
| 多模型投票 | ✅ 通过 |
| 信息流列表 | ✅ 通过 |
| 信息源列表 | ✅ 通过 |
| 知识库列表 | ✅ 通过 |

---

*本文档版本: 1.0*
*最后更新: 2026-03-13*