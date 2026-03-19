-- 自我进化系统数据库迁移
-- Evolution System Migration

-- 创建时间: 2026-03-12

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. 信息源效果指标表
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS source_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
    date DATE NOT NULL,

    -- 数量指标
    total_items INTEGER DEFAULT 0,
    items_fetched INTEGER DEFAULT 0,

    -- 质量指标
    items_read INTEGER DEFAULT 0,
    items_shared INTEGER DEFAULT 0,
    items_to_knowledge INTEGER DEFAULT 0,

    -- 计算指标
    read_rate FLOAT DEFAULT 0.0,
    quality_rate FLOAT DEFAULT 0.0,

    -- 原始数据
    extra JSONB DEFAULT '{}',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_source_metrics_source_date
    ON source_metrics(source_id, date);

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. 潜在信息源表
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS source_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    name VARCHAR(255),
    category VARCHAR(255),

    -- 评估结果
    authority_tier VARCHAR(10),
    ai_score FLOAT,
    content_sample TEXT,

    -- 状态
    status VARCHAR(20) DEFAULT 'pending',
    recommended_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    reject_reason TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_source_candidates_status
    ON source_candidates(status, ai_score DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- 3. 知识质量指标表
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS knowledge_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_base_id VARCHAR(255) NOT NULL,
    document_id VARCHAR(255),

    -- 使用指标
    query_count INTEGER DEFAULT 0,
    relevance_score FLOAT DEFAULT 0.0,
    feedback_score FLOAT DEFAULT 0.0,

    -- 时间
    last_queried TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_metrics_kb
    ON knowledge_metrics(knowledge_base_id, query_count DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- 4. 知识实体表 (知识图谱节点)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS knowledge_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50),
    description TEXT,
    kb_id VARCHAR(255),

    -- 关联
    aliases TEXT[] DEFAULT '{}',
    properties JSONB DEFAULT '{}',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_entities_name
    ON knowledge_entities USING gin(name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_knowledge_entities_type
    ON knowledge_entities(entity_type);

-- ═══════════════════════════════════════════════════════════════════════════
-- 5. 知识关系表 (知识图谱边)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS knowledge_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES knowledge_entities(id) ON DELETE CASCADE,
    target_id UUID REFERENCES knowledge_entities(id) ON DELETE CASCADE,

    relation_type VARCHAR(50) NOT NULL,
    weight FLOAT DEFAULT 1.0,

    evidence TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_relations_source
    ON knowledge_relations(source_id);

CREATE INDEX IF NOT EXISTS idx_knowledge_relations_target
    ON knowledge_relations(target_id);

CREATE INDEX IF NOT EXISTS idx_knowledge_relations_type
    ON knowledge_relations(relation_type);

-- ═══════════════════════════════════════════════════════════════════════════
-- 6. 知识分类表 (层次化分类体系)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS knowledge_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES knowledge_categories(id) ON DELETE SET NULL,
    description TEXT,

    -- 统计
    entity_count INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_categories_parent
    ON knowledge_categories(parent_id);

-- 插入默认分类
INSERT INTO knowledge_categories (name, description) VALUES
    ('人工智能', 'AI/ML 相关知识'),
    ('科技', '技术相关'),
    ('财经', '金融经济'),
    ('商业', '商业创业')
ON CONFLICT DO NOTHING;

-- 添加子分类
INSERT INTO knowledge_categories (name, parent_id, description)
SELECT '大模型', id, 'LLM 相关'
FROM knowledge_categories WHERE name = '人工智能'
ON CONFLICT DO NOTHING;

INSERT INTO knowledge_categories (name, parent_id, description)
SELECT '机器学习', id, 'ML 算法'
FROM knowledge_categories WHERE name = '人工智能'
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════
-- 7. 更新 Source 表添加综合评分字段
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE sources ADD COLUMN IF NOT EXISTS evolution_score FLOAT DEFAULT 50.0;
ALTER TABLE sources ADD COLUMN IF NOT EXISTS last_evaluated_at TIMESTAMP WITH TIME ZONE;

-- ═══════════════════════════════════════════════════════════════════════════
-- 完成
-- ═══════════════════════════════════════════════════════════════════════════

COMMENT ON TABLE source_metrics IS '信息源效果指标 - 追踪每个信息源的实际效果';
COMMENT ON TABLE source_candidates IS '潜在信息源 - 用于新源发现系统';
COMMENT ON TABLE knowledge_metrics IS '知识质量指标 - 追踪知识库内容使用情况';
COMMENT ON TABLE knowledge_entities IS '知识实体 - 知识图谱节点';
COMMENT ON TABLE knowledge_relations IS '知识关系 - 知识图谱边';
COMMENT ON TABLE knowledge_categories IS '知识分类 - 层次化分类体系';