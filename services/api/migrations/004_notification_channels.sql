-- Migration: Add notification_channels table
-- Date: 2026-03-14

CREATE TABLE IF NOT EXISTS notification_channels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,
    webhook_url VARCHAR(500),
    secret VARCHAR(200),
    app_id VARCHAR(100),
    app_secret VARCHAR(200),
    default_target_id VARCHAR(100),
    enabled BOOLEAN DEFAULT TRUE,
    last_test_at TIMESTAMP WITH TIME ZONE,
    last_test_status VARCHAR(20),
    last_test_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Index for querying by type
CREATE INDEX IF NOT EXISTS idx_notification_channels_type ON notification_channels(type);

-- Index for querying enabled channels
CREATE INDEX IF NOT EXISTS idx_notification_channels_enabled ON notification_channels(enabled);