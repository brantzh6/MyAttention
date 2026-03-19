-- Migration: 002_memory.sql
-- Description: Add memory system tables and extend conversation/message tables
-- Date: 2026-02-27

-- Create fact_type enum
DO $$ BEGIN
    CREATE TYPE fact_type AS ENUM ('preference', 'fact', 'decision', 'insight');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Extend conversations table
ALTER TABLE conversations 
    ADD COLUMN IF NOT EXISTS summary TEXT,
    ADD COLUMN IF NOT EXISTS last_message_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS message_count INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS context_window INTEGER DEFAULT 10;

-- Extend messages table
ALTER TABLE messages 
    ADD COLUMN IF NOT EXISTS embedding_id VARCHAR(255),
    ADD COLUMN IF NOT EXISTS is_memory BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS memory_score FLOAT;

-- Create memory_facts table
CREATE TABLE IF NOT EXISTS memory_facts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    fact_type fact_type NOT NULL,
    content TEXT NOT NULL,
    source_conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    source_message_ids UUID[] DEFAULT '{}',
    embedding_id VARCHAR(255),
    confidence FLOAT DEFAULT 0.8,
    category VARCHAR(100),
    tags TEXT[] DEFAULT '{}',
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    valid_until TIMESTAMP WITH TIME ZONE,
    supersedes UUID,
    extra JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create conversation_context table
CREATE TABLE IF NOT EXISTS conversation_context (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    short_term_ids UUID[] DEFAULT '{}',
    long_term_ids UUID[] DEFAULT '{}',
    rag_sources JSONB DEFAULT '[]',
    total_tokens INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for memory_facts
CREATE INDEX IF NOT EXISTS idx_memory_facts_user_id ON memory_facts(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_facts_fact_type ON memory_facts(fact_type);
CREATE INDEX IF NOT EXISTS idx_memory_facts_category ON memory_facts(category);
CREATE INDEX IF NOT EXISTS idx_memory_facts_created_at ON memory_facts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_facts_access_count ON memory_facts(access_count DESC);

-- Create indexes for conversation_context
CREATE INDEX IF NOT EXISTS idx_conversation_context_conversation_id ON conversation_context(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversation_context_message_id ON conversation_context(message_id);

-- Create indexes for messages memory fields
CREATE INDEX IF NOT EXISTS idx_messages_memory_score ON messages(memory_score) WHERE memory_score IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_messages_is_memory ON messages(is_memory) WHERE is_memory = TRUE;

-- Create index for conversations last_message_at
CREATE INDEX IF NOT EXISTS idx_conversations_last_message_at ON conversations(last_message_at DESC);

-- Add trigger for memory_facts updated_at
CREATE OR REPLACE FUNCTION update_memory_facts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_memory_facts_updated_at ON memory_facts;
CREATE TRIGGER trigger_memory_facts_updated_at
    BEFORE UPDATE ON memory_facts
    FOR EACH ROW
    EXECUTE FUNCTION update_memory_facts_updated_at();
