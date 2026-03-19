# 自我进化系统 - 设计文档

## 1. 设计目标

### 1.1 设计原则

1. **自动化优先** - 尽量减少人工干预，系统自动完成闭环
2. **数据驱动** - 所有决策基于实际效果数据
3. **渐进式** - 小步快跑，避免一次性大改
4. **可观测** - 每个决策都有日志和监控
5. **可回滚** - 保留历史，支持回退
6. **AI 增强** - 复杂决策由 AI 驱动，规则作为兜底

### 1.2 架构决策

| 决策项 | 选择 | 理由 |
|-------|------|------|
| 数据存储 | PostgreSQL | 现有基础设施 |
| AI 集成 | 外部 Agent + 本地 LLM + 规则 | 兼顾能力与稳定性 |
| 调度方式 | 后台任务循环 | 简单可靠 |
| 反爬处理 | 获取时即时处理 | 实时响应 |

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           自我进化系统架构                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     入口层 (Auto Evolution System)              │   │
│  │                   feeds/auto_evolution.py                       │   │
│  └─────────────────────────────┬───────────────────────────────────┘   │
│                                │                                        │
│         ┌──────────────────────┼──────────────────────┐                │
│         ▼                      ▼                      ▼                │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐       │
│  │  反爬处理    │    │   AI 决策大脑   │    │   知识图谱       │       │
│  │ anti_crawl  │    │   ai_brain      │    │ knowledge/graph │       │
│  │             │    │                 │    │                 │       │
│  │ - 检测器    │    │ - 外部 Agent   │    │ - 实体提取      │       │
│  │ - 处理器    │    │ - 本地 LLM     │    │ - 关系抽取      │       │
│  │ - 调度器    │    │ - 规则兜底      │    │ - 推理引擎      │       │
│  └──────┬──────┘    └────────┬────────┘    └────────┬────────┘       │
│         │                    │                      │                  │
│         └────────────────────┼──────────────────────┘                  │
│                            ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     进化引擎 (Evolution Engine)                  │   │
│  │                   feeds/evolution.py + metrics.py              │   │
│  │                                                                 │   │
│  │  - 效果评估    - 自适应获取    - 源发现                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                            │                                            │
│         ┌──────────────────┼──────────────────┐                       │
│         ▼                  ▼                  ▼                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
│  │   信息源     │    │   知识库     │    │   外部 AI   │              │
│  │   Sources   │    │ Knowledge   │    │   Agents    │              │
│  │   metrics   │    │  metrics    │    │ (A2A/MCP)  │              │
│  └─────────────┘    └─────────────┘    └─────────────┘              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
┌────────────────────────────────────────────────────────────────────────┐
│                          数据流设计                                      │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  1. 指标收集流程                                                         │
│  ┌─────────┐   ┌─────────────┐   ┌────────────────┐   ┌────────────┐ │
│  │ 信息源   │──▶│ 获取信息    │──▶│ 收集指标       │──▶│ 存储       │ │
│  │ 来源    │   │ RSS/API     │   │ metrics.py    │   │ PostgreSQL │ │
│  └─────────┘   └─────────────┘   └────────────────┘   └────────────┘ │
│                                                                        │
│  2. 反爬处理流程                                                        │
│  ┌─────────┐   ┌─────────────┐   ┌────────────────┐   ┌────────────┐ │
│  │ 获取    │──▶│ 检测反爬    │──▶│ 切换访问方式   │──▶│ 重试成功   │ │
│  │ 请求    │   │ anti_crawl  │   │ PROXY/CLOUD   │   │ ✓         │ │
│  └─────────┘   └─────────────┘   └────────────────┘   └────────────┘ │
│       │              │                                        │       │
│       │              ▼                                        │       │
│       │         ┌─────────────┐                               │       │
│       └────────│ 失败记录     │◀──────────────────────────────┘       │
│                └─────────────┘                                      │
│                                                                        │
│  3. AI 决策流程                                                         │
│  ┌─────────┐   ┌─────────────┐   ┌────────────────┐   ┌────────────┐ │
│  │ 评估    │──▶│ AI 决策     │──▶│ 执行决策       │──▶│ 记录学习   │ │
│  │ 上下文  │   │ ai_brain    │   │ evolution     │   │ 历史      │ │
│  └─────────┘   └─────────────┘   └────────────────┘   └────────────┘ │
│       │              │                                        │       │
│       │         ┌────┴────┐                                   │       │
│       │         ▼         ▼                                   │       │
│       │   ┌─────────┐ ┌─────────┐                            │       │
│       └──│外部Agent│ │本地 LLM │◀────────────────────────────┘       │
│           └─────────┘ └─────────┘                                    │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 数据模型

### 3.1 数据库表

#### 3.1.1 source_metrics (信息源效果指标)

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | UUID | 主键 |
| source_id | UUID | 外键，关联 sources |
| date | DATE | 统计日期 |
| total_items | INT | 获取条目数 |
| items_fetched | INT | 成功获取数 |
| items_read | INT | 被阅读数 |
| items_shared | INT | 转发/收藏数 |
| items_to_knowledge | INT | 转入知识库数 |
| read_rate | FLOAT | 阅读率 |
| quality_rate | FLOAT | 优质率 |
| extra | JSONB | 原始数据 |

#### 3.1.2 source_candidates (潜在信息源)

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | UUID | 主键 |
| url | TEXT | 源 URL |
| name | VARCHAR | 源名称 |
| category | VARCHAR | 分类 |
| authority_tier | VARCHAR | 权威等级 S/A/B/C |
| ai_score | FLOAT | AI 评估分 |
| content_sample | TEXT | 内容样本 |
| status | VARCHAR | pending/recommended/approved/rejected |

#### 3.1.3 knowledge_metrics (知识质量指标)

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | UUID | 主键 |
| knowledge_base_id | VARCHAR | 知识库 ID |
| document_id | VARCHAR | 文档 ID |
| query_count | INT | 被查询次数 |
| relevance_score | FLOAT | 相关性评分 |
| feedback_score | FLOAT | 用户反馈评分 |
| last_queried | TIMESTAMP | 最后查询时间 |

#### 3.1.4 knowledge_entities (知识实体)

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | UUID | 主键 |
| name | VARCHAR | 实体名称 |
| entity_type | VARCHAR | 实体类型 |
| description | TEXT | 描述 |
| kb_id | VARCHAR | 知识库 ID |
| aliases | TEXT[] | 别名 |
| properties | JSONB | 额外属性 |

#### 3.1.5 knowledge_relations (知识关系)

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | UUID | 主键 |
| source_id | UUID | 源实体 |
| target_id | UUID | 目标实体 |
| relation_type | VARCHAR | 关系类型 |
| weight | FLOAT | 权重 |
| evidence | TEXT | 证据 |

#### 3.1.6 knowledge_categories (知识分类)

| 字段 | 类型 | 说明 |
|-----|------|------|
| id | UUID | 主键 |
| name | VARCHAR | 分类名称 |
| parent_id | UUID | 父分类 |
| description | TEXT | 描述 |
| entity_count | INT | 实体数量 |

---

## 4. 模块设计

### 4.1 反爬处理模块 (feeds/anti_crawl.py)

#### 4.1.1 AntiCrawlDetector

**职责**: 检测反爬状态

```python
class AntiCrawlDetector:
    """自动反爬检测器"""

    def detect(self, status_code: int, content: str) -> AntiCrawlStatus:
        """检测反爬状态"""

    def detect_from_error(self, error: Exception) -> AntiCrawlStatus:
        """从异常中检测"""
```

#### 4.1.2 AutomaticAntiCrawlHandler

**职责**: 自动处理反爬

```python
class AutomaticAntiCrawlHandler:
    """自动反爬处理器"""

    async def fetch_with_auto_retry(
        self, url: str, source_id: str, initial_method: AccessMethod
    ) -> AntiCrawlResult:
        """自动重试获取"""

    async def update_source_status(
        self, db, source_id: str, status: AntiCrawlStatus
    ):
        """更新源状态"""
```

#### 4.1.3 AntiCrawlScheduler

**职责**: 定时检查

```python
class AntiCrawlScheduler:
    """反爬调度器"""

    async def _check_all_sources(self):
        """检查所有源"""
```

### 4.2 AI 决策大脑 (feeds/ai_brain.py)

#### 4.2.1 AIDecisionBrain

**职责**: AI 驱动的决策

```python
class AIDecisionBrain:
    """AI 决策大脑"""

    async def decide(self, context: DecisionContext) -> Decision:
        """核心决策方法"""

    async def _get_external_agent(self):
        """获取外部 Agent"""
```

#### 4.2.2 AIEvolutionEngine

**职责**: 驱动源进化

```python
class AIEvolutionEngine:
    """AI 驱动的进化引擎"""

    async def evaluate_and_evolve(self, source_id: str) -> Dict:
        """评估并进化"""
```

### 4.3 外部 Agent 集成 (feeds/external_agent.py)

#### 4.3.1 ExternalAgentClient

**职责**: 调用外部 AI 服务

```python
class ExternalAgentClient:
    """外部 AI Agent 客户端"""

    async def call(
        self, task: str, context: Dict, parameters: Dict
    ) -> AgentResponse:
        """调用外部 Agent"""
```

#### 4.3.2 MyAttentionAIIntegration

**职责**: 统一集成接口

```python
class MyAttentionAIIntegration:
    """MyAttention AI 集成层"""

    async def analyze_problem(self, problem: str, context: Dict) -> AgentResponse:
        """分析问题"""

    async def make_decision(self, decision_type: str, context: Dict) -> AgentResponse:
        """做决策"""

    async def extract_knowledge(self, text: str, context: str) -> AgentResponse:
        """提取知识"""
```

### 4.4 知识图谱 (knowledge/graph.py)

#### 4.4.1 KnowledgeGraphManager

**职责**: 知识图谱管理

```python
class KnowledgeGraphManager:
    """知识图谱管理器"""

    async def process_text(self, text: str, title: str, category: str) -> Dict:
        """处理文本，构建图谱"""

    async def search(self, query: str) -> GraphQueryResult:
        """搜索"""

    async def reason(self, entity: str, target_type: str) -> List[str]:
        """推理"""
```

---

## 5. 接口设计

### 5.1 进化引擎接口

```python
# feeds/evolution.py

class SourceEvolutionEngine:
    """源进化引擎"""

    async def get_source_scorecard(self, source_id: str) -> Optional[SourceScorecard]:
        """获取计分卡"""

    async def evaluate_and_evolve(self, source_id: str) -> EvolutionResult:
        """评估并进化"""

    async def evolve_all_sources(self) -> List[EvolutionResult]:
        """批量进化"""
```

### 5.2 调度接口

```python
# pipeline/evolution_scheduler.py

class EvolutionScheduler:
    """进化调度器"""

    async def run_source_evaluation(self) -> Dict:
        """运行源效果评估"""

    async def run_adaptive_fetching(self) -> Dict:
        """运行自适应获取"""

    async def run_full_cycle(self) -> Dict:
        """运行完整周期"""
```

---

## 6. 配置设计

### 6.1 环境变量

| 变量 | 说明 | 默认值 |
|-----|------|-------|
| AGENT_ENDPOINT | 外部 Agent 端点 | http://localhost:8080 |
| AGENT_API_KEY | API 密钥 | - |
| AGENT_PROTOCOL | 协议类型 | a2a |
| EVOLUTION_INTERVAL | 进化间隔(秒) | 3600 |
| CHECK_INTERVAL | 检查间隔(秒) | 1800 |

### 6.2 调度配置

```python
@dataclass
class SchedulerConfig:
    source_evaluation_interval: int = 7  # 天
    knowledge_evaluation_interval: int = 7
    source_discovery_interval: int = 30
    evaluation_hour: int = 2
    enable_auto_evolution: bool = True
```

---

## 7. 依赖关系

```
feeds/
├── anti_crawl.py      # 依赖: db/models
├── ai_brain.py        # 依赖: external_agent, db/models
├── evolution.py       # 依赖: db/models, authority
├── metrics.py         # 依赖: db/models
├── auto_evolution.py  # 依赖: 上述所有模块
└── external_agent.py  # 依赖: aiohttp

knowledge/
└── graph.py           # 依赖: db/models

pipeline/
└── evolution_scheduler.py  # 依赖: evolution, ai_brain
```

---

*本文档版本: 1.0*
*最后更新: 2026-03-12*