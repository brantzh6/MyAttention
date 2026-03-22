"""
Database Models - SQLAlchemy ORM definitions
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
import enum

from sqlalchemy import (
    Column, String, Text, Boolean, Float, Integer, 
    DateTime, ForeignKey, Enum, JSON, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


# Enums
class SourceType(str, enum.Enum):
    RSS = "rss"
    WEB = "web"
    API = "api"


class SourceStatus(str, enum.Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    DISABLED = "disabled"


class AuthorityTier(str, enum.Enum):
    """信息源权威等级"""
    S = "S"  # 权威官方
    A = "A"  # 行业头部
    B = "B"  # 社区平台
    C = "C"  # 待评估


class AccessMethod(str, enum.Enum):
    """信息获取方式"""
    DIRECT = "direct"    # 直接访问
    PROXY = "proxy"      # 代理访问
    CLOUD = "cloud"      # 云手机/云服务
    MANUAL = "manual"    # 手动处理


class AntiCrawlStatus(str, enum.Enum):
    """反爬状态"""
    OK = "ok"
    BLOCKED = "blocked"          # 被封禁
    RATE_LIMITED = "rate_limited"  # 限速
    PAYWALL = "paywall"          # 付费墙
    CAPTCHA = "captcha"         # 验证码
    UNKNOWN = "unknown"


SourceTypeDbEnum = Enum(
    SourceType,
    name="source_type",
    create_type=False,
    values_callable=lambda x: [e.value for e in x]
)

SourceStatusDbEnum = Enum(
    SourceStatus,
    name="source_status",
    create_type=False,
    values_callable=lambda x: [e.value for e in x]
)

AccessMethodDbEnum = Enum(
    AccessMethod,
    name="access_method",
    create_type=False,
    values_callable=lambda x: [e.value for e in x]
)

AntiCrawlStatusDbEnum = Enum(
    AntiCrawlStatus,
    name="anti_crawl_status",
    create_type=False,
    values_callable=lambda x: [e.value for e in x]
)


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# PostgreSQL enum type for MessageRole
MessageRoleEnum = Enum(
    MessageRole,
    name="message_role",
    create_type=False,
    values_callable=lambda x: [e.value for e in x]
)

class DecisionStatus(str, enum.Enum):
    DRAFT = "draft"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class NotificationChannelType(str, enum.Enum):
    FEISHU = "feishu"
    DINGTALK = "dingtalk"
    EMAIL = "email"
    WEBHOOK = "webhook"


class FactType(str, enum.Enum):
    """Memory fact types"""
    PREFERENCE = "preference"  # User preferences
    FACT = "fact"              # Important facts
    DECISION = "decision"      # Decision records
    INSIGHT = "insight"        # Insights and summaries


# PostgreSQL enum type for FactType (match database type name, use lowercase values)
FactTypeEnum = Enum(
    FactType, 
    name="fact_type", 
    create_type=False,
    values_callable=lambda x: [e.value for e in x]
)


# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True)
    name = Column(String(255))
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    sources = relationship("Source", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="user", cascade="all, delete-orphan")
    memory_facts = relationship("MemoryFact", back_populates="user", cascade="all, delete-orphan")


class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    type = Column(SourceTypeDbEnum, nullable=False)
    url = Column(Text, nullable=False)
    category = Column(String(255))
    tags = Column(ARRAY(Text), default=list)
    priority = Column(String(50), default="medium")
    enabled = Column(Boolean, default=True)
    status = Column(SourceStatusDbEnum, default=SourceStatus.OK)
    config = Column(JSON, default=dict)
    last_fetched_at = Column(DateTime(timezone=True))
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # === 新增：权威分级 ===
    authority_tier = Column(String(10), default="B")  # S, A, B, C
    authority_score = Column(Float, default=0.5)        # 0-1 权威评分

    # === 新增：访问能力 ===
    access_method = Column(AccessMethodDbEnum, default=AccessMethod.DIRECT)
    requires_auth = Column(Boolean, default=False)
    auth_config = Column(JSON, default=dict)  # cookies, headers等

    # === 新增：内容深度 ===
    fetch_depth = Column(Integer, default=1)  # 1=摘要, 2=全文, 3=分析
    last_deep_fetched = Column(DateTime(timezone=True))

    # === 新增：反爬状态 ===
    anti_crawl_status = Column(AntiCrawlStatusDbEnum, default=AntiCrawlStatus.OK)
    retry_count = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="sources")
    feed_items = relationship("FeedItem", back_populates="source", cascade="all, delete-orphan")
    knowledge_links = relationship("KnowledgeLink", back_populates="source", cascade="all, delete-orphan")


class FeedItem(Base):
    __tablename__ = "feed_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"))
    external_id = Column(String(512))
    title = Column(Text, nullable=False)
    summary = Column(Text)
    content = Column(Text)
    url = Column(Text)
    author = Column(String(255))
    importance = Column(Float, default=0.5)
    published_at = Column(DateTime(timezone=True))
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    embedding_id = Column(String(255))
    extra = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # === 新增：知识提取 ===
    is_knowledge_extracted = Column(Boolean, default=False)
    knowledge_tags = Column(ARRAY(Text), default=list)
    extracted_summary = Column(Text)  # L3 深度摘要

    # Relationships
    source = relationship("Source", back_populates="feed_items")
    interactions = relationship("FeedItemInteraction", back_populates="feed_item", cascade="all, delete-orphan")
    knowledge_links = relationship("KnowledgeLink", back_populates="feed_item", cascade="all, delete-orphan")


class RawIngest(Base):
    __tablename__ = "raw_ingest"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_key = Column(String(255), nullable=False)
    external_id = Column(String(512))
    object_key = Column(Text, nullable=False, unique=True)
    storage_backend = Column(String(50), nullable=False, default="local")
    content_type = Column(String(255))
    content_encoding = Column(String(100))
    content_hash = Column(String(128), nullable=False)
    size_bytes = Column(Integer, nullable=False, default=0)
    fetched_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    http_status = Column(Integer)
    access_method = Column(String(50))
    proxy_used = Column(Boolean, default=False)
    anti_crawl_status = Column(String(50))
    request_meta = Column(JSON, default=dict)
    response_meta = Column(JSON, default=dict)
    parse_status = Column(String(50), default="pending")
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FeedItemInteraction(Base):
    __tablename__ = "feed_item_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    feed_item_id = Column(UUID(as_uuid=True), ForeignKey("feed_items.id", ondelete="CASCADE"))
    is_read = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    feed_item = relationship("FeedItem", back_populates="interactions")


class KnowledgeLink(Base):
    """信息到知识的关联表"""
    __tablename__ = "knowledge_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    feed_item_id = Column(UUID(as_uuid=True), ForeignKey("feed_items.id", ondelete="CASCADE"))
    knowledge_base_id = Column(String(255), nullable=False)  # 知识库ID (字符串)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    linked_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="pending")  # pending, confirmed, rejected
    notes = Column(Text)  # 用户备注

    # Relationships
    feed_item = relationship("FeedItem", back_populates="knowledge_links")
    source = relationship("Source", back_populates="knowledge_links")


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255))
    model = Column(String(255))
    use_voting = Column(Boolean, default=False)
    summary = Column(Text)                    # AI-generated conversation summary
    last_message_at = Column(DateTime(timezone=True))  # Last message timestamp
    message_count = Column(Integer, default=0)  # Total message count
    context_window = Column(Integer, default=10)  # Short-term context window size
    extra = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    memory_facts = relationship("MemoryFact", back_populates="source_conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(MessageRoleEnum, nullable=False)
    content = Column(Text, nullable=False)
    model = Column(String(255))
    tokens_used = Column(Integer)
    sources = Column(JSON, default=list)
    voting_results = Column(JSON)
    embedding_id = Column(String(255))        # Qdrant vector ID (for important messages)
    is_memory = Column(Boolean, default=False)  # Whether extracted as long-term memory
    memory_score = Column(Float)              # Memory importance score (0-1)
    extra = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class LLMProvider(Base):
    __tablename__ = "llm_providers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)
    model = Column(String(255), nullable=False)
    api_key_encrypted = Column(Text)
    base_url = Column(Text)
    enabled = Column(Boolean, default=True)
    priority = Column(String(50), default="medium")
    use_cases = Column(ARRAY(Text), default=list)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class LLMVotingConfig(Base):
    __tablename__ = "llm_voting_config"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    enabled = Column(Boolean, default=True)
    model_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)
    consensus_threshold = Column(Float, default=0.67)
    max_cost = Column(Float)
    timeout_seconds = Column(Integer, default=60)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    decision_type = Column(String(100))
    status = Column(Enum(DecisionStatus), default=DecisionStatus.DRAFT)
    analysis_report = Column(Text)
    sources_used = Column(JSON, default=list)
    models_used = Column(JSON, default=list)
    voting_results = Column(JSON)
    confidence = Column(Float)
    outcome = Column(String(255))
    outcome_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="decisions")


class NotificationChannel(Base):
    __tablename__ = "notification_channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)  # 存储为字符串: feishu, dingtalk, email, webhook
    webhook_url = Column(Text)

    # App API 模式配置 (飞书/钉钉)
    app_id = Column(String(100))
    app_secret = Column(String(200))
    default_target_id = Column(String(100))

    # 签名密钥 (钉钉)
    secret = Column(String(200))

    config = Column(JSON, default=dict)
    enabled = Column(Boolean, default=True)
    last_test_at = Column(DateTime(timezone=True))
    last_test_status = Column(String(50))
    last_test_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    author = Column(String(255))
    tags = Column(ARRAY(Text), default=list)
    prompt_template = Column(Text)
    config = Column(JSON, default=dict)
    enabled = Column(Boolean, default=True)
    is_builtin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    provider = Column(String(100))
    model = Column(String(255))
    tokens_input = Column(Integer)
    tokens_output = Column(Integer)
    cost = Column(Float)
    task_type = Column(String(100))
    latency_ms = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MemoryFact(Base):
    """Long-term memory facts extracted from conversations"""
    __tablename__ = "memory_facts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    fact_type = Column(FactTypeEnum, nullable=False)
    content = Column(Text, nullable=False)           # Memory content
    source_conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"))
    source_message_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)  # Related message IDs
    embedding_id = Column(String(255))               # Qdrant vector ID
    confidence = Column(Float, default=0.8)          # Confidence score (0-1)
    category = Column(String(100))                   # Category label
    tags = Column(ARRAY(Text), default=list)         # Tags
    access_count = Column(Integer, default=0)        # Access count
    last_accessed_at = Column(DateTime(timezone=True))  # Last access time
    valid_until = Column(DateTime(timezone=True))    # Expiration time (null=permanent)
    supersedes = Column(UUID(as_uuid=True))          # ID of superseded memory
    extra = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="memory_facts")
    source_conversation = relationship("Conversation", back_populates="memory_facts")


class ConversationContext(Base):
    """Records context used for each conversation turn (for debugging)"""
    __tablename__ = "conversation_context"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"))
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"))
    short_term_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)  # Short-term message IDs used
    long_term_ids = Column(ARRAY(UUID(as_uuid=True)), default=list)   # Long-term memory IDs used
    rag_sources = Column(JSON, default=list)         # RAG retrieval sources
    total_tokens = Column(Integer)                   # Total context tokens
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ═══════════════════════════════════════════════════════════════════════════
# 自我进化系统模型 (Evolution System)
# ═══════════════════════════════════════════════════════════════════════════

class SourceMetrics(Base):
    """信息源效果指标 - 追踪每个信息源的实际效果"""
    __tablename__ = "source_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"))
    date = Column(DateTime(timezone=True), nullable=False)  # 统计日期

    # 数量指标
    total_items = Column(Integer, default=0)       # 获取条目数
    items_fetched = Column(Integer, default=0)     # 成功获取数

    # 质量指标
    items_read = Column(Integer, default=0)       # 被阅读数
    items_shared = Column(Integer, default=0)     # 转发/收藏数
    items_to_knowledge = Column(Integer, default=0)  # 转入知识库数

    # 计算指标
    read_rate = Column(Float, default=0.0)         # 阅读率
    quality_rate = Column(Float, default=0.0)      # 优质率

    # 原始数据（用于详细分析）
    extra = Column(JSON, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source = relationship("Source", backref="metrics")


class SourceCandidate(Base):
    """潜在信息源 - 用于新源发现系统"""
    __tablename__ = "source_candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    url = Column(Text, nullable=False)
    name = Column(String(255))
    category = Column(String(255))

    # 评估结果
    authority_tier = Column(String(10))  # S, A, B, C
    ai_score = Column(Float)              # AI 评估分
    content_sample = Column(Text)         # 内容样本

    # 状态
    status = Column(String(20), default="pending")  # pending, recommended, approved, rejected
    recommended_at = Column(DateTime(timezone=True))
    approved_at = Column(DateTime(timezone=True))
    rejected_at = Column(DateTime(timezone=True))
    reject_reason = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class KnowledgeMetrics(Base):
    """知识质量指标 - 追踪知识库内容使用情况"""
    __tablename__ = "knowledge_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    knowledge_base_id = Column(String(255), nullable=False)
    document_id = Column(String(255))

    # 使用指标
    query_count = Column(Integer, default=0)         # 被查询次数
    relevance_score = Column(Float, default=0.0)   # 相关性评分
    feedback_score = Column(Float, default=0.0)    # 用户反馈评分

    # 时间
    last_queried = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class KnowledgeEntity(Base):
    """知识实体 - 知识图谱节点"""
    __tablename__ = "knowledge_entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    entity_type = Column(String(50))  # person, org, concept, tech, event, location
    description = Column(Text)
    kb_id = Column(String(255))

    # 关联
    aliases = Column(ARRAY(Text), default=list)  # 别名
    properties = Column(JSON, default=dict)      # 额外属性

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    source_relations = relationship(
        "KnowledgeRelation",
        foreign_keys="KnowledgeRelation.source_id",
        back_populates="source_entity",
        cascade="all, delete-orphan"
    )
    target_relations = relationship(
        "KnowledgeRelation",
        foreign_keys="KnowledgeRelation.target_id",
        back_populates="target_entity",
        cascade="all, delete-orphan"
    )


class KnowledgeRelation(Base):
    """知识关系 - 知识图谱边"""
    __tablename__ = "knowledge_relations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_entities.id", ondelete="CASCADE"))
    target_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_entities.id", ondelete="CASCADE"))

    relation_type = Column(String(50), nullable=False)  # related_to, part_of, caused_by, owns, etc.
    weight = Column(Float, default=1.0)                  # 关系权重

    evidence = Column(Text)                             # 关系证据
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    source_entity = relationship("KnowledgeEntity", foreign_keys=[source_id], back_populates="source_relations")
    target_entity = relationship("KnowledgeEntity", foreign_keys=[target_id], back_populates="target_relations")


class KnowledgeCategory(Base):
    """知识分类 - 层次化分类体系"""
    __tablename__ = "knowledge_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_categories.id", ondelete="SET NULL"))
    description = Column(Text)

    # 统计
    entity_count = Column(Integer, default=0)  # 该分类下的实体数

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Self-referential relationship for hierarchy
    children = relationship("KnowledgeCategory", backref="parent", remote_side=[id])


# ═══════════════════════════════════════════════════════════════════════════
# 任务系统模型 (Task System)
# ═══════════════════════════════════════════════════════════════════════════

class TaskPriority(int, enum.Enum):
    """任务优先级"""
    P0_URGENT = 0    # 紧急 - 自动处理
    P1_IMPORTANT = 1  # 重要 - 需人工确认
    P2_NORMAL = 2    # 普通 - 汇总报告
    P3_SUGGESTION = 3  # 建议 - 定期汇总


class TaskStatus(str, enum.Enum):
    """任务状态"""
    PENDING = "pending"           # 待处理
    CONFIRMED = "confirmed"       # 已确认（待执行）
    REJECTED = "rejected"         # 已拒绝
    EXECUTING = "executing"       # 执行中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    EXPIRED = "expired"           # 已过期


class TaskSourceType(str, enum.Enum):
    """任务来源类型"""
    API_TEST = "api_test"         # API测试
    UI_TEST = "ui_test"          # UI测试
    ANTI_CRAWL = "anti_crawl"    # 反爬检测
    SOURCE_EVOLUTION = "source_evolution"  # 信息源演化
    KNOWLEDGE_QUALITY = "knowledge_quality"  # 知识质量
    SYSTEM_HEALTH = "system_health"  # 系统健康


class TaskCategory(str, enum.Enum):
    """任务分类"""
    FUNCTIONAL = "functional"     # 功能问题
    PERFORMANCE = "performance"   # 性能问题
    SECURITY = "security"         # 安全问题
    CONFIG = "config"             # 配置问题
    QUALITY = "quality"           # 质量问题
    SUGGESTION = "suggestion"    # 优化建议


class TaskAction(str, enum.Enum):
    """任务处理动作"""
    AUTO_RETRY = "auto_retry"     # 自动重试
    MANUAL_CONFIRM = "manual_confirm"  # 人工确认
    AUTO_FIX = "auto_fix"         # 自动修复
    CONFIRM = "confirm"           # 确认执行
    REJECT = "reject"             # 拒绝
    EXECUTE = "execute"           # 执行


class TaskType(str, enum.Enum):
    """Task classes for the V1 workflow model."""
    DAEMON = "daemon"
    WORKFLOW = "workflow"
    UNIT = "unit"
    REFINEMENT = "refinement"


class ContextStatus(str, enum.Enum):
    """Lifecycle states for long-lived contexts."""
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ContextType(str, enum.Enum):
    """Top-level context categories."""
    EVOLUTION = "evolution"
    CHAT = "chat"
    RESEARCH = "research"
    SOURCE_INTELLIGENCE = "source_intelligence"
    KNOWLEDGE = "knowledge"
    SYSTEM = "system"


class ArtifactType(str, enum.Enum):
    """Structured task outputs."""
    REPORT = "report"
    SCREENSHOT = "screenshot"
    STRUCTURED_DIAGNOSIS = "structured_diagnosis"
    REPAIR_PLAN = "repair_plan"
    RESEARCH_BRIEF = "research_brief"
    EVIDENCE_LOG = "evidence_log"
    KNOWLEDGE_EXTRACTION = "knowledge_extraction"
    TIMELINE = "timeline"
    COMPARISON = "comparison"
    DECISION_SUMMARY = "decision_summary"


class RelationType(str, enum.Enum):
    """Relations between contexts, tasks, and artifacts."""
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    DEPENDS_ON = "depends_on"
    BLOCKED_BY = "blocked_by"
    REFINES = "refines"
    HANDOFF_TO = "handoff_to"
    PRODUCED = "produced"
    REVIEWS = "reviews"
    RETRIES = "retries"
    SUPERSEDES = "supersedes"


class BrainRole(str, enum.Enum):
    """Brain roles in the control plane."""
    CHIEF = "chief"
    DIALOG = "dialog"
    SOURCE_INTELLIGENCE = "source_intelligence"
    RESEARCH = "research"
    KNOWLEDGE = "knowledge"
    EVOLUTION = "evolution"
    CODING = "coding"
    SYSTEM = "system"


class Task(Base):
    """任务表 - 存储系统检测到的问题和待处理任务"""
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # 来源信息
    source_type = Column(String(50), nullable=False)  # api_test, ui_test, anti_crawl, etc.
    source_id = Column(String(255))  # 来源ID
    source_data = Column(JSON, default=dict)  # 原始数据

    # 任务内容
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # 优先级和分类
    priority = Column(Integer, default=2)  # 0=紧急, 1=重要, 2=普通, 3=建议
    category = Column(String(50))  # functional, performance, security, config
    context_id = Column(UUID(as_uuid=True), ForeignKey("task_contexts.id", ondelete="SET NULL"))
    task_type = Column(String(50), default=TaskType.WORKFLOW.value)
    goal = Column(Text)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"))
    initiator_type = Column(String(50))
    initiator_id = Column(String(255))
    assigned_brain = Column(String(100))
    assigned_agent = Column(String(100))
    budget_policy = Column(JSON, default=dict)
    timeout_policy = Column(JSON, default=dict)
    retry_policy = Column(JSON, default=dict)

    # 状态
    status = Column(String(20), default="pending")

    # 处理方式
    auto_processible = Column(Boolean, default=False)
    auto_process_config = Column(JSON, default=dict)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    confirmed_at = Column(DateTime(timezone=True))
    rejected_at = Column(DateTime(timezone=True))
    executing_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    expired_at = Column(DateTime(timezone=True))
    checkpoint_ref = Column(String(255))
    result_summary = Column(Text)

    # 创建者
    created_by = Column(String(100), default="system")

    # Relationships
    context = relationship("TaskContext", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[id], backref="child_tasks")
    history = relationship("TaskHistory", back_populates="task", cascade="all, delete-orphan")
    artifacts = relationship("TaskArtifact", back_populates="task", cascade="all, delete-orphan")


class TaskHistory(Base):
    """任务处理历史 - 记录每个任务的处理过程"""
    __tablename__ = "task_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True,
    )

    # 处理信息
    action = Column(String(50), nullable=False)  # auto_retry, manual_confirm, auto_fix, confirm, reject
    result = Column(String(50), nullable=False)  # success, failed, skipped, timeout

    # 详细信息
    context_id = Column(UUID(as_uuid=True), ForeignKey("task_contexts.id", ondelete="SET NULL"))
    event_type = Column(String(50))
    from_status = Column(String(20))
    to_status = Column(String(20))
    reason = Column(Text)
    details = Column(JSON, default=dict)
    payload = Column(JSON, default=dict)

    # 执行者
    performed_by = Column(String(100), default="system")

    # 时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    context = relationship("TaskContext", back_populates="events")
    task = relationship("Task", back_populates="history")


class TaskContext(Base):
    """Long-lived contexts that group related tasks."""
    __tablename__ = "task_contexts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    context_type = Column(String(50), nullable=False, default=ContextType.SYSTEM.value)
    title = Column(String(255), nullable=False)
    goal = Column(Text)
    owner_type = Column(String(50))
    owner_id = Column(String(255))
    status = Column(String(20), nullable=False, default=ContextStatus.ACTIVE.value)
    priority = Column(Integer, default=2)
    extra = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))

    tasks = relationship("Task", back_populates="context")
    events = relationship("TaskHistory", back_populates="context")
    artifacts = relationship("TaskArtifact", back_populates="context")


class TaskArtifact(Base):
    """Structured artifacts produced by tasks."""
    __tablename__ = "task_artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    context_id = Column(UUID(as_uuid=True), ForeignKey("task_contexts.id", ondelete="CASCADE"))
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True,
    )
    artifact_type = Column(String(50), nullable=False)
    version = Column(Integer, default=1)
    parent_version = Column(Integer)
    title = Column(String(255), nullable=False)
    summary = Column(Text)
    storage_ref = Column(Text)
    content_ref = Column(Text)
    created_by = Column(String(100), default="system")
    extra = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    context = relationship("TaskContext", back_populates="artifacts")
    task = relationship("Task", back_populates="artifacts")


class TaskRelation(Base):
    """Relations between contexts, tasks, and artifacts."""
    __tablename__ = "task_relations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_type = Column(String(50), nullable=False)
    source_id = Column(String(255), nullable=False)
    relation_type = Column(String(50), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(255), nullable=False)
    extra = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BrainProfile(Base):
    """Brain control plane profile."""
    __tablename__ = "brain_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    brain_id = Column(String(100), nullable=False, unique=True)
    role = Column(String(50), nullable=False)
    description = Column(Text)
    capabilities = Column(ARRAY(Text), default=list)
    default_models = Column(JSON, default=list)
    fallback_models = Column(JSON, default=list)
    tool_policy = Column(JSON, default=dict)
    cost_policy = Column(JSON, default=dict)
    latency_policy = Column(JSON, default=dict)
    risk_policy = Column(JSON, default=dict)
    status = Column(String(20), default="active")
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    routes_as_primary = relationship(
        "BrainRoute",
        foreign_keys="BrainRoute.primary_brain_id",
        back_populates="primary_brain",
    )
    routes_as_review = relationship(
        "BrainRoute",
        foreign_keys="BrainRoute.review_brain_id",
        back_populates="review_brain",
    )
    routes_as_fallback = relationship(
        "BrainRoute",
        foreign_keys="BrainRoute.fallback_brain_id",
        back_populates="fallback_brain",
    )


class BrainRoute(Base):
    """Routing rules from problem types to brains."""
    __tablename__ = "brain_routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    route_id = Column(String(100), nullable=False, unique=True)
    problem_type = Column(String(100), nullable=False)
    thinking_framework = Column(String(100))
    primary_brain_id = Column(UUID(as_uuid=True), ForeignKey("brain_profiles.id", ondelete="CASCADE"))
    supporting_brains = Column(ARRAY(Text), default=list)
    review_brain_id = Column(UUID(as_uuid=True), ForeignKey("brain_profiles.id", ondelete="SET NULL"))
    fallback_brain_id = Column(UUID(as_uuid=True), ForeignKey("brain_profiles.id", ondelete="SET NULL"))
    version = Column(Integer, default=1)
    enabled = Column(Boolean, default=True)
    extra = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    primary_brain = relationship("BrainProfile", foreign_keys=[primary_brain_id], back_populates="routes_as_primary")
    review_brain = relationship("BrainProfile", foreign_keys=[review_brain_id], back_populates="routes_as_review")
    fallback_brain = relationship("BrainProfile", foreign_keys=[fallback_brain_id], back_populates="routes_as_fallback")


class BrainPolicy(Base):
    """Execution and risk policy for a brain or route."""
    __tablename__ = "brain_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id = Column(String(100), nullable=False, unique=True)
    brain_id = Column(String(100))
    route_id = Column(String(100))
    cost_policy = Column(JSON, default=dict)
    latency_policy = Column(JSON, default=dict)
    execution_policy = Column(JSON, default=dict)
    network_policy = Column(JSON, default=dict)
    timeout_policy = Column(JSON, default=dict)
    degrade_policy = Column(JSON, default=dict)
    enabled = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BrainFallback(Base):
    """Fallback rules when a primary brain is unavailable."""
    __tablename__ = "brain_fallbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    fallback_id = Column(String(100), nullable=False, unique=True)
    brain_id = Column(String(100), nullable=False)
    failure_mode = Column(String(100), nullable=False)
    fallback_brain = Column(String(100))
    fallback_mode = Column(String(100), default="degrade")
    fallback_policy = Column(JSON, default=dict)
    enabled = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SourcePlan(Base):
    """Topic-driven source intelligence plan."""
    __tablename__ = "source_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    topic = Column(String(255), nullable=False)
    focus = Column(String(50), nullable=False, default="authoritative")
    objective = Column(Text)
    owner_type = Column(String(50), default="system")
    owner_id = Column(String(255))
    planning_brain = Column(String(100), default="source-intelligence-brain")
    status = Column(String(20), default="active")
    review_status = Column(String(20), default="pending")
    review_cadence_days = Column(Integer, default=14)
    current_version = Column(Integer, default=1)
    latest_version = Column(Integer, default=1)
    extra = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    items = relationship("SourcePlanItem", back_populates="plan", cascade="all, delete-orphan")
    versions = relationship("SourcePlanVersion", back_populates="plan", cascade="all, delete-orphan")


class SourcePlanItem(Base):
    """Concrete source objects and monitoring decisions inside a source plan."""
    __tablename__ = "source_plan_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("source_plans.id", ondelete="CASCADE"))
    item_type = Column(String(50), default="domain")
    object_key = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(Text)
    authority_tier = Column(String(10))
    authority_score = Column(Float, default=0.0)
    monitoring_mode = Column(String(50), default="review")
    execution_strategy = Column(String(50), default="search_review")
    review_cadence_days = Column(Integer, default=14)
    rationale = Column(Text)
    evidence = Column(JSON, default=dict)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    plan = relationship("SourcePlan", back_populates="items")


class SourcePlanVersion(Base):
    """Versioned review snapshots for source plans."""
    __tablename__ = "source_plan_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("source_plans.id", ondelete="CASCADE"))
    version_number = Column(Integer, nullable=False)
    parent_version = Column(Integer)
    trigger_type = Column(String(50), default="manual_refresh")
    decision_status = Column(String(20), default="accepted")
    change_reason = Column(Text)
    change_summary = Column(JSON, default=dict)
    plan_snapshot = Column(JSON, default=dict)
    evaluation = Column(JSON, default=dict)
    created_by = Column(String(100), default="system")
    accepted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    plan = relationship("SourcePlan", back_populates="versions")


class TaskMemory(Base):
    """Scoped memory for task and context recovery."""
    __tablename__ = "task_memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    context_id = Column(UUID(as_uuid=True), ForeignKey("task_contexts.id", ondelete="CASCADE"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"))
    memory_kind = Column(String(50), nullable=False, default="checkpoint")
    title = Column(String(255), nullable=False)
    summary = Column(Text)
    content = Column(Text)
    created_by = Column(String(100), default="system")
    extra = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ProceduralMemory(Base):
    """Validated methods, playbooks, and operating procedures."""
    __tablename__ = "procedural_memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    memory_key = Column(String(100), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    problem_type = Column(String(100))
    thinking_framework = Column(String(100))
    method_name = Column(String(100))
    applicability = Column(Text)
    procedure = Column(Text)
    effectiveness_score = Column(Float, default=0.0)
    validation_status = Column(String(20), default="draft")
    source_kind = Column(String(50), default="system")
    source_ref = Column(String(255))
    version = Column(Integer, default=1)
    parent_version = Column(Integer)
    last_validated_at = Column(DateTime(timezone=True))
    extra = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
