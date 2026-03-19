-- MyAttention Database Schema
-- Initial migration: Core tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================
-- User and Settings
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key VARCHAR(255) NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, key)
);

-- ============================================
-- Information Sources
-- ============================================

CREATE TYPE source_type AS ENUM ('rss', 'web', 'api');
CREATE TYPE source_status AS ENUM ('ok', 'warning', 'error', 'disabled');

CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type source_type NOT NULL,
    url TEXT NOT NULL,
    category VARCHAR(255),
    tags TEXT[] DEFAULT '{}',
    priority VARCHAR(50) DEFAULT 'medium',
    enabled BOOLEAN DEFAULT true,
    status source_status DEFAULT 'ok',
    config JSONB DEFAULT '{}',
    last_fetched_at TIMESTAMP WITH TIME ZONE,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sources_user_id ON sources(user_id);
CREATE INDEX idx_sources_type ON sources(type);
CREATE INDEX idx_sources_enabled ON sources(enabled);

-- ============================================
-- Feed Items
-- ============================================

CREATE TABLE feed_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
    external_id VARCHAR(512),
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    url TEXT,
    author VARCHAR(255),
    importance FLOAT DEFAULT 0.5,
    published_at TIMESTAMP WITH TIME ZONE,
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    embedding_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, external_id)
);

CREATE INDEX idx_feed_items_source_id ON feed_items(source_id);
CREATE INDEX idx_feed_items_published_at ON feed_items(published_at DESC);
CREATE INDEX idx_feed_items_importance ON feed_items(importance DESC);

-- User interactions with feed items
CREATE TABLE feed_item_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    feed_item_id UUID REFERENCES feed_items(id) ON DELETE CASCADE,
    is_read BOOLEAN DEFAULT false,
    is_favorite BOOLEAN DEFAULT false,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, feed_item_id)
);

CREATE INDEX idx_feed_item_interactions_user ON feed_item_interactions(user_id);

-- ============================================
-- Conversations and Messages
-- ============================================

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    model VARCHAR(255),
    use_voting BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    model VARCHAR(255),
    tokens_used INTEGER,
    sources JSONB DEFAULT '[]',
    voting_results JSONB,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- ============================================
-- LLM Configuration
-- ============================================

CREATE TABLE llm_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    model VARCHAR(255) NOT NULL,
    api_key_encrypted TEXT,
    base_url TEXT,
    enabled BOOLEAN DEFAULT true,
    priority VARCHAR(50) DEFAULT 'medium',
    use_cases TEXT[] DEFAULT '{}',
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_llm_providers_user_id ON llm_providers(user_id);
CREATE INDEX idx_llm_providers_enabled ON llm_providers(enabled);

CREATE TABLE llm_routing_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    task_type VARCHAR(100) NOT NULL,
    primary_provider_id UUID REFERENCES llm_providers(id),
    fallback_provider_id UUID REFERENCES llm_providers(id),
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, task_type)
);

CREATE TABLE llm_voting_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT true,
    model_ids UUID[] DEFAULT '{}',
    consensus_threshold FLOAT DEFAULT 0.67,
    max_cost DECIMAL(10, 4),
    timeout_seconds INTEGER DEFAULT 60,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- ============================================
-- Decision Analysis
-- ============================================

CREATE TYPE decision_status AS ENUM ('draft', 'analyzing', 'completed', 'archived');

CREATE TABLE decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    decision_type VARCHAR(100),
    status decision_status DEFAULT 'draft',
    analysis_report TEXT,
    sources_used JSONB DEFAULT '[]',
    models_used JSONB DEFAULT '[]',
    voting_results JSONB,
    confidence FLOAT,
    outcome VARCHAR(255),
    outcome_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_decisions_user_id ON decisions(user_id);
CREATE INDEX idx_decisions_status ON decisions(status);
CREATE INDEX idx_decisions_created_at ON decisions(created_at DESC);

-- ============================================
-- Notifications
-- ============================================

CREATE TYPE notification_channel_type AS ENUM ('feishu', 'dingtalk', 'email', 'webhook');

CREATE TABLE notification_channels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type notification_channel_type NOT NULL,
    webhook_url TEXT,
    config JSONB DEFAULT '{}',
    enabled BOOLEAN DEFAULT true,
    last_test_at TIMESTAMP WITH TIME ZONE,
    last_test_status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notification_channels_user_id ON notification_channels(user_id);

CREATE TABLE notification_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel_id UUID REFERENCES notification_channels(id) ON DELETE CASCADE,
    title VARCHAR(255),
    content TEXT,
    status VARCHAR(50),
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notification_history_channel_id ON notification_history(channel_id);
CREATE INDEX idx_notification_history_sent_at ON notification_history(sent_at DESC);

-- ============================================
-- Skills (Reserved)
-- ============================================

CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    author VARCHAR(255),
    tags TEXT[] DEFAULT '{}',
    prompt_template TEXT,
    config JSONB DEFAULT '{}',
    enabled BOOLEAN DEFAULT true,
    is_builtin BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_skills_name ON skills(name);
CREATE INDEX idx_skills_enabled ON skills(enabled);

-- ============================================
-- Usage Tracking
-- ============================================

CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(100),
    model VARCHAR(255),
    tokens_input INTEGER,
    tokens_output INTEGER,
    cost DECIMAL(10, 6),
    task_type VARCHAR(100),
    latency_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at DESC);
CREATE INDEX idx_usage_logs_provider ON usage_logs(provider);

-- ============================================
-- Default Data
-- ============================================

-- Insert default user
INSERT INTO users (id, email, name) VALUES 
    ('00000000-0000-0000-0000-000000000001', 'default@myattention.local', 'Default User');

-- Insert default notification channels
INSERT INTO notification_channels (user_id, name, type, enabled) VALUES
    ('00000000-0000-0000-0000-000000000001', '飞书通知', 'feishu', false),
    ('00000000-0000-0000-0000-000000000001', '钉钉通知', 'dingtalk', false);

-- Insert builtin skills
INSERT INTO skills (name, version, description, author, is_builtin, prompt_template) VALUES
    ('summarize', '1.0.0', '智能摘要生成', 'system', true, 
     '请将以下内容整理成结构化摘要：\n{{content}}\n\n要求：\n- 提取关键信息\n- 分点列出\n- 不超过{{max_length}}字'),
    ('analyze', '1.0.0', '深度分析', 'system', true,
     '请对以下内容进行深度分析：\n{{content}}\n\n要求：\n- 多角度分析\n- 给出结论和建议\n- 标注置信度');

-- ============================================
-- Updated_at Trigger Function
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_feed_item_interactions_updated_at BEFORE UPDATE ON feed_item_interactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_llm_providers_updated_at BEFORE UPDATE ON llm_providers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_llm_routing_rules_updated_at BEFORE UPDATE ON llm_routing_rules FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_llm_voting_config_updated_at BEFORE UPDATE ON llm_voting_config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_decisions_updated_at BEFORE UPDATE ON decisions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_notification_channels_updated_at BEFORE UPDATE ON notification_channels FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON skills FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
