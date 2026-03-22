# MyAttention 文档规范

> 所有功能开发必须遵循本规范进行文档记录
> 本规范是 MyAttention 项目开发的强制要求

---

## 1. 文档类型

MyAttention 项目使用以下三类文档：

| 文档类型 | 文件命名 | 说明 |
|---------|---------|------|
| **PROJECT_MASTER_PLAN.md** | 项目总计划 | 项目主线、模块框架、研发运作规则 |
| **CHANGELOG.md** | 项目变更日志 | 项目级重要改动、阶段能力提升、兼容性调整 |
| **SPEC.md** | 需求规格说明书 | 需求分析、功能描述、用户故事 |
| **设计文档** | `<功能名>_DESIGN.md` | 架构设计、数据模型、接口设计 |
| **实现文档** | `<功能名>_IMPLEMENTATION.md` | 代码实现细节、API 说明 |

专项架构设计也可使用语义化命名，例如：

- `FEED_DATA_ARCHITECTURE.md`
- `STORAGE_ARCHITECTURE.md`
- `ENGINEERING_METHOD.md`
- `ENCODING_AND_I18N_STANDARD.md`
- `CHANGE_MANAGEMENT.md`
- `VERSION_MANAGEMENT.md`
- `GSTACK_TRIAL_PLAN.md`
- `SKILL_EVALUATION_LOG.md`
- `PROJECT_EXECUTION_ROADMAP.md`
- `DEPLOYMENT_RUN_MODES.md`
- `DEPLOYMENT_AUTOMATION_DESIGN.md`
- `KNOWLEDGE_ARCHITECTURE.md`

---

## 2. 文档模板

### 2.1 需求规格说明书 (SPEC.md)

```markdown
# [功能名称] - 需求规格说明书

## 1. 概述
- 功能简介
- 解决的问题
- 目标用户

## 2. 功能需求
- 功能列表
- 用户故事

## 3. 非功能需求
- 性能要求
- 安全要求
- 兼容性

## 4. 验收标准
- 功能验收
- 测试用例
```

### 2.2 设计文档

```markdown
# [功能名称] - 设计文档

## 1. 设计目标
- 设计原则
- 架构决策

## 2. 系统架构
- 架构图
- 组件设计

## 3. 数据模型
- 数据库表
- 数据结构

## 4. 接口设计
- API 接口
- 事件设计

## 5. 依赖关系
- 依赖模块
- 外部服务
```

### 2.3 实现文档

```markdown
# [功能名称] - 实现文档

## 1. 实现概述
- 技术栈
- 文件结构

## 2. 核心模块
- 模块说明
- 代码示例

## 3. API 接口
- 接口列表
- 请求/响应格式

## 4. 配置说明
- 环境变量
- 配置文件

## 5. 部署指南
- 依赖安装
- 迁移脚本
```

---

## 3. 文档位置

```
MyAttention/
├── docs/
│   ├── SPEC.md                    # 项目总体规格说明书
│   ├── ARCHITECTURE.md            # 系统架构文档
│   │
│   ├── evolution/                 # 自我进化系统文档
│   │   ├── evolution_SPEC.md
│   │   ├── evolution_DESIGN.md
│   │   └── evolution_IMPLEMENTATION.md
│   │
│   ├── ai_integration/            # AI 集成文档
│   │   ├── ai_spec.md
│   │   ├── ai_design.md
│   │   └── ai_implementation.md
│   │
│   └── ...
│
├── migrations/                     # 数据库迁移
├── services/api/                   # 后端代码
└── services/web/                   # 前端代码
```

---

## 4. 文档更新规则

| 场景 | 要求 |
|-----|------|
| 新功能开发 | 必须先对齐 `PROJECT_MASTER_PLAN.md`，再创建或更新 SPEC、DESIGN、IMPLEMENTATION 文档 |
| 功能修改 | 更新对应的实现文档，说明变更原因 |
| Bug 修复 | 在实现文档中添加问题描述和修复方案 |
| 重构 | 更新设计文档，说明重构原因和影响 |
| 中大型改造 | 必须先形成方案并落设计文档，经确认后再编码 |
| L2/L3 变更 | 必须更新 `CHANGELOG.md`，必要时补充 `docs/CHANGE_MANAGEMENT.md` 对应记录 |

---

## 4.1 研发流程强制要求

后续研发默认遵守以下流程：

1. 先确认目标、边界和主线优先级
2. 先补充方案或设计文档
3. 方案确认后再编码
4. 编码后必须做验证
5. 结果必须更新到进度或实现文档中

---

## 5. 文档审查

- 代码提交前必须完成文档更新
- 文档应包含足够的细节以供他人理解
- 文档中的架构图应使用文本或 PlantUML 格式

---

## 6. 示例

### 示例：自我进化系统文档结构

```
docs/evolution/
├── evolution_SPEC.md       # 需求：为什么做、做什么
├── evolution_DESIGN.md     # 设计：怎么做、架构是什么
└── evolution_IMPLEMENTATION.md  # 实现：具体代码、API
```

每个文档的具体内容请参考对应模板。

---

*本规范自 2026-03-12 起执行*
