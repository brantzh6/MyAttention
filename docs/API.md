# MyAttention API Documentation

## 自我进化系统 - 任务处理与决策架构

### 概述

自我进化系统是一个智能任务处理与决策架构，能够：
- 自动收集和分析系统日志
- 识别错误模式并生成改进建议
- 根据优先级自动处理或请求人工确认
- 定时监控系统健康状态
- 实时监控问题，支持秒级告警

---

## 快速开始

### 实时健康检查 (秒级响应)

```bash
# 快速检查 - 5分钟内发现问题
GET /api/evolution/health/quick

# 问题中心仪表盘 - 一目了然
GET /api/evolution/dashboard/problems

# 立即触发分析
POST /api/evolution/health/check-now
```

### 问题处理流程

```
发现问题 → 自动创建任务 → 通知 → 人工/自动处理 → 记录解决方案
```

---

## API 端点

### 实时监控 API

#### 快速健康检查 (秒级)
```bash
GET /api/evolution/health/quick
```
响应时间: <100ms

响应示例：
```json
{
  "status": "healthy",
  "checked_at": "2026-03-14T11:40:55",
  "logs_checked": 388,
  "critical_issues": [],
  "critical_count": 0,
  "response_time_ms": 15
}
```

#### 问题中心仪表盘
```bash
GET /api/evolution/dashboard/problems
```

#### 立即触发分析
```bash
POST /api/evolution/health/check-now
```

#### 获取紧急问题
```bash
GET /api/evolution/problems/urgent
```

#### 解决问题
```bash
POST /api/evolution/problems/{task_id}/resolve
Content-Type: application/json
{
  "resolution": "已通过重启服务解决"
}
```

---

### 任务管理 API

#### 创建任务
```bash
POST /api/evolution/tasks
Content-Type: application/json

{
  "source_type": "api_test",
  "title": "任务标题",
  "description": "任务描述",
  "priority": 1,
  "category": "performance",
  "auto_processible": false
}
```

#### 获取任务列表
```bash
GET /api/evolution/tasks?priority=1&status=pending&limit=20
```

#### 获取任务详情
```bash
GET /api/evolution/tasks/{task_id}
```

#### 执行任务操作
```bash
POST /api/evolution/tasks/{task_id}/action
Content-Type: application/json

{
  "action": "confirm"  # confirm, reject, execute
  "reason": "原因描述"
}
```

#### 获取任务历史
```bash
GET /api/evolution/tasks/{task_id}/history
```

#### 任务统计摘要
```bash
GET /api/evolution/tasks/stats/summary
```

#### 从测试结果创建任务
```bash
POST /api/evolution/tasks/from-test-result?test_type=api_test
Content-Type: application/json
{
  "endpoint": "/api/feeds",
  "status_code": 500,
  "error": "Internal Server Error"
}
```

---

### 日志监控与分析 API

#### 健康摘要
```bash
GET /api/evolution/logs/health?hours=24
```

#### 详细日志分析
```bash
POST /api/evolution/logs/analyze
Content-Type: application/json

{
  "source": "api",        # api, chat, web_api, web_frontend (optional)
  "hours": 24,           # 回溯小时数
  "level": "ERROR"       # ERROR, WARNING, INFO (optional)
}
```

#### 系统洞察建议
```bash
GET /api/evolution/logs/insights?category=performance&severity=warning&hours=24
```

#### 错误模式统计
```bash
GET /api/evolution/logs/errors?hours=24&limit=20
```

#### 性能指标
```bash
GET /api/evolution/logs/metrics?hours=24
```

#### 实时日志
```bash
GET /api/evolution/logs/recent?source=api&level=ERROR&hours=1&limit=100
```

#### 洞察转任务
```bash
POST /api/evolution/logs/insights/{insight_id}/to-task
```

---

### 其他 API

#### 触发进化周期
```bash
POST /api/evolution/trigger
```

#### 获取进化状态
```bash
GET /api/evolution/status
```

#### 评估信息源
```bash
POST /api/evolution/sources/evaluate
Content-Type: application/json
{
  "source_id": "uuid"
}
```

#### 反爬测试
```bash
POST /api/evolution/anti-crawl/test
Content-Type: application/json
{
  "url": "https://example.com",
  "method": "direct"
}
```

#### 知识图谱搜索
```bash
POST /api/evolution/knowledge/search
Content-Type: application/json
{
  "query": "search term",
  "max_results": 20
}
```

---

## 问题处理流程

### 问题来源

1. **自动检测**
   - 日志分析发现错误
   - 反爬被拦截
   - 测试失败
   - 定时健康检查

2. **手动创建**
   - 用户通过 API 创建
   - 从洞察建议转化

### 问题生命周期

```
┌─────────────────────────────────────────────────────────────┐
│                    问题生命周期                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 发现                                                   │
│     ├── 自动发现（每小时日志分析）                          │
│     ├── 手动触发（/health/quick 秒级检查）                 │
│     └── 用户报告                                           │
│          │                                                 │
│          ▼                                                 │
│  2. 创建任务                                               │
│     ├── P0 (紧急) → 自动处理                               │
│     ├── P1 (重要) → 发送通知，等待确认                     │
│     ├── P2 (普通) → 添加到汇总报告                         │
│     └── P3 (建议) → 定期汇总                               │
│          │                                                 │
│          ▼                                                 │
│  3. 处理                                                   │
│     ├── 自动处理 → 重试、切换策略                          │
│     ├── 人工确认 → 执行任务                                 │
│     └── 拒绝 → 记录原因                                    │
│          │                                                 │
│          ▼                                                 │
│  4. 解决                                                   │
│     └── 记录解决方案 → 完成任务                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 问题存储

- **tasks 表**: 所有问题/任务
- **task_history 表**: 处理历史
- **日志文件**: 原始日志

### 查看问题

1. **问题中心仪表盘**: `/api/evolution/dashboard/problems`
2. **紧急问题列表**: `/api/evolution/problems/urgent`
3. **任务列表**: `/api/evolution/tasks`

---

## 自动工作流程

### 日志监控系统自动工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                    日志监控系统                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐ │
│  │  定时触发   │───▶│  收集日志    │───▶│  错误模式分析 │ │
│  │ (每1小时)   │    │ (最近24小时) │    │  识别问题类型  │ │
│  └─────────────┘    └──────────────┘    └───────────────┘ │
│         │                                         │         │
│         │                                         ▼         │
│         │                                   ┌───────────────┐ │
│         │                                   │ 生成洞察建议  │ │
│         │                                   │ - 问题描述    │ │
│         │                                   │ - 证据        │ │
│         │                                   │ - 改进建议    │ │
│         │                                   └───────────────┘ │
│         │                                         │         │
│         ▼                                         ▼         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    决策处理                              │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  critical → 自动创建P0任务 → 自动处理                   │ │
│  │  warning  → 自动创建P1任务 → 发送通知 → 等待确认        │ │
│  │  info    → 添加到每日汇总报告                          │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  实时告警:                                                  │
│  - 手动调用 /health/quick (秒级响应)                        │
│  - 自动每小时分析 + 即时问题检测                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 与任务系统集成

```
日志分析发现错误
       │
       ▼
┌──────────────────┐
│ 生成 SystemInsight│
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────┐
│        自动决策                        │
├──────────────────────────────────────┤
│  severity=critical → 自动创建Task(P0) │
│                              ↓        │
│                        自动执行       │
├──────────────────────────────────────┤
│  severity=warning → 自动创建Task(P1)  │
│                              ↓        │
│                        发送飞书通知   │
│                              ↓        │
│                      用户确认后执行   │
├──────────────────────────────────────┤
│  severity=info → 添加到每日报告       │
└──────────────────────────────────────┘
```

### 实时告警

```
用户需要快速检查
       │
       ▼
┌──────────────────┐
│ /health/quick   │
│ (秒级响应<100ms)│
└────────┬─────────┘
         │
    返回关键信息：
    - status: healthy/critical
    - critical_issues: 问题列表
    - response_time_ms: 响应时间
```

---

## 问题处理示例

### 1. 快速检查系统状态

```bash
# 秒级健康检查
curl http://localhost:8000/api/evolution/health/quick

# 问题中心仪表盘
curl http://localhost:8000/api/evolution/dashboard/problems
```

### 2. 查看紧急问题

```bash
curl http://localhost:8000/api/evolution/problems/urgent
```

### 3. 手动触发分析

```bash
curl -X POST http://localhost:8000/api/evolution/health/check-now
```

### 4. 处理任务

```bash
# 确认并执行
curl -X POST http://localhost:8000/api/evolution/tasks/{task_id}/action \
  -H "Content-Type: application/json" \
  -d '{"action":"confirm"}'

# 解决问题
curl -X POST http://localhost:8000/api/evolution/problems/{task_id}/resolve \
  -H "Content-Type: application/json" \
  -d '{"resolution":"已通过重启服务解决"}'
```