# MyAttention 测试文档

> 测试要求是项目交付门槛，不是补充项。总体研发流程与约束见：`docs/PROJECT_MASTER_PLAN.md`，项目级研发方法与质量体系见：`docs/ENGINEERING_METHOD.md`

## 测试策略概览

```
┌─────────────────────────────────────────────────────────────┐
│                      测试金字塔                              │
├─────────────────────────────────────────────────────────────┤
│                        /\                                   │
│                       /  \        E2E 测试                  │
│                      /────\      (Playwright)               │
│                     /      \                                 │
│                    /────────\    集成测试                    │
│                   /          \   (API 测试)                  │
│                  /────────────\                              │
│                 /              \ 单元测试                    │
│                /────────────────\(pytest, jest)             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. 单元测试

### 1.1 后端单元测试 (pytest)

**测试框架**: pytest + pytest-asyncio

**目录结构**:
```
services/api/
├── tests/
│   ├── conftest.py           # 测试配置和 fixtures
│   ├── test_llm_adapter.py   # LLM 适配器测试
│   ├── test_kb_manager.py    # 知识库管理器测试
│   ├── test_memory.py        # 记忆引擎测试
│   └── test_routers/         # API 路由测试
│       ├── test_chat.py
│       ├── test_rag.py
│       └── test_conversations.py
```

**示例测试**:

```python
# tests/test_kb_manager.py
import pytest
from knowledge import KnowledgeBaseManager, Document

@pytest.fixture
def kb_manager():
    return KnowledgeBaseManager()

@pytest.mark.asyncio
async def test_create_knowledge_base(kb_manager):
    """测试创建知识库"""
    kb = await kb_manager.create_knowledge_base(
        name="测试知识库",
        description="用于测试"
    )
    assert kb.id is not None
    assert kb.name == "测试知识库"

@pytest.mark.asyncio
async def test_add_document(kb_manager):
    """测试添加文档"""
    kb = await kb_manager.create_knowledge_base("test")
    doc = Document(
        id="test-doc",
        content="这是一段测试内容",
        title="测试文档",
        source="test"
    )
    chunk_ids = await kb_manager.add_document(doc, kb.id)
    assert len(chunk_ids) > 0

@pytest.mark.asyncio
async def test_search(kb_manager):
    """测试搜索功能"""
    results = await kb_manager.search(
        query="测试",
        kb_id="test",
        limit=5
    )
    assert isinstance(results, list)
```

**运行测试**:
```bash
cd services/api
pytest tests/ -v --cov=. --cov-report=html
```

### 1.2 前端单元测试 (Jest)

**测试框架**: Jest + React Testing Library

**目录结构**:
```
services/web/
├── __tests__/
│   ├── components/
│   │   ├── ChatInterface.test.tsx
│   │   └── KnowledgeBaseManager.test.tsx
│   └── lib/
│       └── api-client.test.ts
```

**示例测试**:

```typescript
// __tests__/lib/api-client.test.ts
import { apiClient } from '@/lib/api-client';

// Mock fetch
global.fetch = jest.fn();

describe('apiClient', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  test('getKnowledgeBases should fetch KBs', async () => {
    const mockData = { knowledge_bases: [] };
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData)
    });

    const result = await apiClient.getKnowledgeBases();
    expect(result).toEqual(mockData);
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/rag/knowledge-bases')
    );
  });
});
```

**运行测试**:
```bash
cd services/web
npm test
npm run test:coverage
```

---

## 2. 集成测试 (API 测试)

### 2.1 API 端点测试

**使用 pytest + httpx**:

```python
# tests/test_routers/test_chat.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_chat_endpoint(client):
    """测试聊天端点"""
    response = await client.post(
        "/api/chat",
        json={
            "message": "你好",
            "use_rag": False
        }
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_knowledge_bases_endpoint(client):
    """测试知识库列表端点"""
    response = await client.get("/api/rag/knowledge-bases")
    assert response.status_code == 200
    data = response.json()
    assert "knowledge_bases" in data
```

### 2.2 数据库集成测试

```python
# tests/test_db.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from db.models import Base, User, Conversation

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session

@pytest.mark.asyncio
async def test_create_user(db_session):
    """测试创建用户"""
    user = User(email="test@example.com", name="Test")
    db_session.add(user)
    await db_session.commit()

    assert user.id is not None
```

---

## 3. E2E 测试 (Playwright)

### 3.1 安装配置

```bash
npm install -D @playwright/test
npx playwright install
```

### 3.2 测试用例

```typescript
// e2e/chat.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Chat Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3001/chat');
  });

  test('should display chat input', async ({ page }) => {
    await expect(page.locator('textarea')).toBeVisible();
  });

  test('should send message and receive response', async ({ page }) => {
    // 输入消息
    await page.fill('textarea', '你好');
    await page.click('button[type="submit"]');

    // 等待响应
    await page.waitForSelector('.assistant-message', { timeout: 30000 });

    // 验证响应
    const response = page.locator('.assistant-message').first();
    await expect(response).toBeVisible();
  });

  test('should toggle knowledge base search', async ({ page }) => {
    // 点击知识库开关
    const kbToggle = page.locator('button:has-text("知识库")');
    await kbToggle.click();

    // 验证状态变化
    await expect(kbToggle).toHaveClass(/bg-emerald/);
  });
});

test.describe('Knowledge Base Manager', () => {
  test('should list knowledge bases', async ({ page }) => {
    await page.goto('http://localhost:3001/settings/knowledge');

    // 等待知识库列表加载
    await page.waitForSelector('[data-testid="kb-list"]');

    // 验证列表存在
    const kbList = page.locator('[data-testid="kb-list"]');
    await expect(kbList).toBeVisible();
  });
});
```

### 3.3 运行 E2E 测试

```bash
# 启动测试
npx playwright test

# 带界面运行
npx playwright test --ui

# 生成报告
npx playwright show-report
```

---

## 4. 性能测试

### 4.1 负载测试 (Locust)

```python
# locustfile.py
from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def chat(self):
        self.client.post("/api/chat", json={
            "message": "测试消息",
            "use_rag": False
        })

    @task(3)
    def list_knowledge_bases(self):
        self.client.get("/api/rag/knowledge-bases")
```

**运行负载测试**:
```bash
locust -f locustfile.py --host http://localhost:8000
```

### 4.2 性能基准

| 端点 | 目标响应时间 | 并发数 |
|------|-------------|--------|
| POST /api/chat (首token) | < 3s | 10 |
| GET /api/rag/knowledge-bases | < 500ms | 50 |
| GET /api/conversations | < 500ms | 50 |
| POST /api/rag/knowledge-bases/{id}/search | < 2s | 10 |

---

## 5. 测试数据管理

### 5.1 测试数据准备

```python
# tests/conftest.py
import pytest
from uuid import uuid4
from db import get_db, User, Conversation, Message

@pytest.fixture
async def test_user(db_session):
    """创建测试用户"""
    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Test User"
    )
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture
async def test_conversation(db_session, test_user):
    """创建测试对话"""
    conv = Conversation(
        id=uuid4(),
        user_id=test_user.id,
        title="测试对话"
    )
    db_session.add(conv)
    await db_session.commit()
    return conv
```

### 5.2 数据清理

```python
@pytest.fixture(autouse=True)
async def cleanup(db_session):
    """每个测试后清理数据"""
    yield
    # 清理测试数据
    await db_session.rollback()
```

---

## 6. Mock 策略

### 6.1 LLM API Mock

```python
# tests/mocks/llm.py
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_llm_stream():
    """Mock LLM 流式响应"""
    async def mock_stream(*args, **kwargs):
        yield "你好"
        yield "，这是"
        yield "测试响应"

    with patch('llm.adapter.LLMAdapter.stream_chat', return_value=mock_stream()):
        yield
```

### 6.2 向量数据库 Mock

```python
# tests/mocks/qdrant.py
@pytest.fixture
def mock_qdrant():
    """Mock Qdrant 客户端"""
    with patch('qdrant_client.QdrantClient') as mock:
        mock.return_value.search.return_value = []
        yield mock
```

---

## 7. CI/CD 集成

### 7.1 GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd services/api
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run tests
        run: |
          cd services/api
          pytest tests/ -v --cov=. --cov-report=xml
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test_db

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd services/web
          npm ci

      - name: Run tests
        run: |
          cd services/web
          npm run test:coverage
```

---

## 8. 测试覆盖率目标

| 模块 | 目标覆盖率 | 当前状态 |
|------|-----------|----------|
| LLM Adapter | 80% | 待测试 |
| KB Manager | 80% | 待测试 |
| Memory Engine | 70% | 待测试 |
| API Routers | 80% | 待测试 |
| Frontend Components | 70% | 待测试 |

---

## 9. 测试命令速查

```bash
# 后端单元测试
cd services/api && pytest tests/ -v

# 后端覆盖率
cd services/api && pytest tests/ --cov=. --cov-report=html

# 前端单元测试
cd services/web && npm test

# 前端覆盖率
cd services/web && npm run test:coverage

# E2E 测试
npx playwright test

# 负载测试
locust -f locustfile.py

# 类型检查 (mypy)
cd services/api && mypy .

# 代码风格 (ruff)
cd services/api && ruff check .
```

---

## 10. 测试最佳实践

### 10.1 原则

1. **测试隔离**: 每个测试独立，不依赖其他测试
2. **数据清理**: 测试后清理创建的数据
3. **Mock 外部依赖**: 不要在测试中调用真实 API
4. **有意义的断言**: 断言应该验证业务逻辑

### 10.2 命名规范

```python
# 测试函数命名: test_<功能>_<场景>_<预期结果>
def test_chat_with_rag_enabled_returns_sources():
    pass

def test_create_kb_with_empty_name_raises_error():
    pass
```

### 10.3 测试组织

```python
class TestKnowledgeBaseManager:
    """知识库管理器测试组"""

    @pytest.mark.asyncio
    async def test_create(self):
        """测试创建"""
        pass

    @pytest.mark.asyncio
    async def test_delete(self):
        """测试删除"""
        pass

    @pytest.mark.asyncio
    async def test_search(self):
        """测试搜索"""
        pass
```
