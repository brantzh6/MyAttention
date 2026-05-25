-- Migration: 007_add_extra_columns.sql
-- Description: Add extra JSONB columns to conversations and messages tables
--              to align schema with SQLAlchemy ORM models
-- Note: GIN indexes intentionally omitted from this hotfix to avoid table locking
--        on busy tables. Indexes can be added separately during maintenance windows.
-- Date: 2026-05-25

-- Add extra column to conversations table
ALTER TABLE conversations
ADD COLUMN IF NOT EXISTS extra JSONB DEFAULT '{}';

-- Add extra column to messages table
ALTER TABLE messages
ADD COLUMN IF NOT EXISTS extra JSONB DEFAULT '{}';
