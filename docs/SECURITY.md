# MyAttention 安全文档

## 安全架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                      安全层次架构                            │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: 网络安全                                           │
│  ├── CORS 配置                                               │
│  ├── Rate Limiting (待实现)                                  │
│  └── HTTPS (生产环境)                                        │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: 应用安全                                           │
│  ├── 输入验证                                                │
│  ├── 输出编码                                                │
│  ├── 错误处理                                                │
│  └── 日志审计                                                │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: 数据安全                                           │
│  ├── API Key 加密存储                                        │
│  ├── 数据库访问控制                                          │
│  └── 向量数据隔离                                            │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: API 安全                                           │
│  ├── 第三方 API Key 管理                                     │
│  ├── 请求签名 (待实现)                                       │
│  └── 调用监控                                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. API Key 安全

### 1.1 存储方式

**当前实现**:
- API Key 通过环境变量配置
- 存储在 `.env` 文件中（不纳入版本控制）

**生产环境建议**:
```python
# 使用加密存储
class LLMProvider(Base):
    api_key_encrypted = Column(Text)  # 加密后的 Key
```

### 1.2 使用规范

```bash
# .env 文件 (不要提交到 Git)
QWEN_API_KEY=sk-xxxxxxxxxxxxx
GLM_API_KEY=xxxxxxxxxxxxxxxxx

# 通过环境变量注入
export QWEN_API_KEY="sk-xxxxx"
```

### 1.3 风险缓解

| 风险 | 缓解措施 |
|------|----------|
| Key 泄露 | 使用环境变量，不硬编码 |
| 日志泄露 | 日志中脱敏 API Key |
| 传输窃取 | 生产环境使用 HTTPS |

---

## 2. 输入验证

### 2.1 Pydantic 模型验证

所有 API 输入使用 Pydantic 模型：

```python
class ChatRequest(BaseModel):
    message: str                    # 必填字符串
    conversation_id: Optional[str]  # 可选字符串
    use_voting: bool = False        # 布尔默认值
    enable_search: bool = False
    kb_ids: Optional[List[str]]     # 可选字符串列表
```

### 2.2 文件上传验证

```python
# 文件类型白名单
SUPPORTED_EXTENSIONS = {
    '.txt': 'text/plain',
    '.md': 'text/markdown',
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument...',
    '.html': 'text/html',
}

def is_supported(filename: str) -> bool:
    ext = Path(filename).suffix.lower()
    return ext in SUPPORTED_EXTENSIONS
```

### 2.3 URL 验证

```python
# URL 格式验证
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
```

---

## 3. 数据安全

### 3.1 数据库安全

**连接安全**:
```python
# 使用连接池
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/db"

# 生产环境建议
# - 使用 SSL 连接
# - 限制数据库用户权限
# - 定期备份
```

**查询安全**:
```python
# 使用 SQLAlchemy ORM (防 SQL 注入)
query = select(Conversation).where(
    Conversation.id == conv_uuid,
    Conversation.user_id == DEFAULT_USER_ID
)
```

### 3.2 向量数据隔离

**知识库隔离**:
- 每个知识库对应独立的 Qdrant Collection
- Collection 命名: `kb_{kb_id}`

**数据隔离**:
```python
# 搜索时指定知识库
results = await kb_manager.search(
    query=query,
    kb_id=kb_id,  # 仅搜索指定知识库
    limit=5
)
```

### 3.3 用户数据隔离

**当前状态**:
- 使用默认用户 ID（单用户模式）
- 所有数据关联到同一用户

**多用户扩展**:
```python
# 预留的用户隔离字段
class Conversation(Base):
    user_id = Column(UUID, ForeignKey("users.id"))
```

---

## 4. 网络安全

### 4.1 CORS 配置

**开发环境**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**生产环境建议**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # 限制来源
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### 4.2 Rate Limiting (待实现)

```python
# 建议实现
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/chat")
@limiter.limit("30/minute")  # 每分钟 30 次
async def chat(request: ChatRequest):
    pass
```

---

## 5. LLM 安全

### 5.1 Prompt 注入防护

**风险**: 用户输入恶意 Prompt 干扰系统指令

**缓解措施**:
```python
# 系统指令优先
system_prompt = "你是 MyAttention 智能助手..."

# 用户输入作为数据，不作为指令
user_message = request.message  # 仅作为数据传递
```

### 5.2 输出过滤

**敏感信息过滤**:
- 日志中脱敏 API Key
- 不在前端展示完整配置

### 5.3 费用控制

**使用监控**:
```python
class UsageLog(Base):
    tokens_input = Column(Integer)
    tokens_output = Column(Integer)
    cost = Column(Float)
```

**预算限制** (待实现):
- 设置每日/每月调用上限
- 超限自动熔断

---

## 6. 日志与审计

### 6.1 日志记录

```python
# 聊天日志
_chat_logger = logging.getLogger("myattention.chat")
_chat_logger.setLevel(logging.DEBUG)

# 文件日志
_fh = logging.FileHandler("chat_debug.log", encoding="utf-8")
```

### 6.2 审计追踪

**记录内容**:
- 请求时间
- 用户 ID
- 模型选择
- Token 使用量
- 响应状态

```python
class UsageLog(Base):
    user_id = Column(UUID)
    provider = Column(String)
    model = Column(String)
    tokens_input = Column(Integer)
    tokens_output = Column(Integer)
    created_at = Column(DateTime)
```

---

## 7. 依赖安全

### 7.1 依赖管理

**requirements.txt**:
```
fastapi>=0.100.0
uvicorn>=0.23.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
httpx>=0.24.0
qdrant-client>=1.4.0
sentence-transformers>=2.2.0
```

### 7.2 安全更新

```bash
# 检查安全漏洞
pip-audit

# 更新依赖
pip install --upgrade -r requirements.txt
```

---

## 8. 安全检查清单

### 开发阶段

- [ ] 不在代码中硬编码密钥
- [ ] 不提交 `.env` 文件
- [ ] 使用参数化查询防止 SQL 注入
- [ ] 验证所有用户输入
- [ ] 错误信息不泄露敏感信息

### 部署阶段

- [ ] 启用 HTTPS
- [ ] 配置防火墙规则
- [ ] 限制数据库访问
- [ ] 配置日志轮转
- [ ] 设置备份策略

### 运维阶段

- [ ] 定期更新依赖
- [ ] 监控异常请求
- [ ] 审计日志分析
- [ ] 密钥轮换策略

---

## 9. 安全事件响应

### 事件级别

| 级别 | 描述 | 响应时间 |
|------|------|----------|
| P0 | API Key 泄露 | 立即 |
| P1 | 数据泄露 | 24小时内 |
| P2 | 服务异常 | 48小时内 |
| P3 | 潜在漏洞 | 一周内 |

### 响应流程

```
发现事件 → 评估影响 → 遏制措施 → 根除威胁 → 恢复服务 → 复盘总结
```

---

## 10. 合规性说明

### 数据处理

- **数据收集**: 仅收集必要数据
- **数据存储**: 本地存储，不上传第三方
- **数据使用**: 仅用于服务功能

### 第三方服务

| 服务 | 数据类型 | 用途 |
|------|----------|------|
| 阿里云 Qwen | 对话内容 | LLM 推理 |
| 智谱 GLM | 对话内容 | LLM 推理 |
| 阿里云 IQS | 搜索关键词 | 网络搜索 |

**注意**: 用户对话内容会发送到第三方 LLM 服务，请勿输入敏感信息。