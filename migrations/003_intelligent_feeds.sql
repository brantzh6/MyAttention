-- 智能信息获取系统迁移
-- 添加权威分级、访问能力、深度获取、知识链接等功能

-- 1. 添加新的 enum 类型
DO $$ BEGIN
    CREATE TYPE authority_tier AS ENUM ('S', 'A', 'B', 'C');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE access_method AS ENUM ('direct', 'proxy', 'cloud', 'manual');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE anti_crawl_status AS ENUM ('ok', 'blocked', 'rate_limited', 'paywall', 'captcha', 'unknown');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. 扩展 sources 表
ALTER TABLE sources
ADD COLUMN IF NOT EXISTS authority_tier VARCHAR(10) DEFAULT 'B',
ADD COLUMN IF NOT EXISTS authority_score FLOAT DEFAULT 0.5,
ADD COLUMN IF NOT EXISTS access_method access_method DEFAULT 'direct',
ADD COLUMN IF NOT EXISTS requires_auth BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS auth_config JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS fetch_depth INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS last_deep_fetched TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS anti_crawl_status anti_crawl_status DEFAULT 'ok',
ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;

-- 3. 扩展 feed_items 表
ALTER TABLE feed_items
ADD COLUMN IF NOT EXISTS is_knowledge_extracted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS knowledge_tags TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS extracted_summary TEXT;

-- 4. 创建 knowledge_links 表
CREATE TABLE IF NOT EXISTS knowledge_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feed_item_id UUID REFERENCES feed_items(id) ON DELETE CASCADE,
    knowledge_base_id VARCHAR(255) NOT NULL,
    source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    linked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending',
    notes TEXT
);

-- 5. 创建索引
CREATE INDEX IF NOT EXISTS idx_sources_authority_tier ON sources(authority_tier);
CREATE INDEX IF NOT EXISTS idx_sources_access_method ON sources(access_method);
CREATE INDEX IF NOT EXISTS idx_feed_items_knowledge_extracted ON feed_items(is_knowledge_extracted);
CREATE INDEX IF NOT EXISTS idx_knowledge_links_feed_item ON knowledge_links(feed_item_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_links_kb ON knowledge_links(knowledge_base_id);