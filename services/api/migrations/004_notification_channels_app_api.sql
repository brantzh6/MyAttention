-- Migration: Add App API columns to notification_channels
-- Created: 2026-03-14

-- Check if columns exist and add if they don't
DO $$
BEGIN
    -- Add app_id column if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'notification_channels' AND column_name = 'app_id') THEN
        ALTER TABLE notification_channels ADD COLUMN app_id VARCHAR(100);
    END IF;

    -- Add app_secret column if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'notification_channels' AND column_name = 'app_secret') THEN
        ALTER TABLE notification_channels ADD COLUMN app_secret VARCHAR(200);
    END IF;

    -- Add default_target_id column if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'notification_channels' AND column_name = 'default_target_id') THEN
        ALTER TABLE notification_channels ADD COLUMN default_target_id VARCHAR(100);
    END IF;
END $$;