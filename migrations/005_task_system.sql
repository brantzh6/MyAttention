-- 任务系统数据库迁移
-- Task System Migration
-- 创建时间: 2026-03-13

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. 任务表 (tasks)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 来源信息
    source_type VARCHAR(50) NOT NULL,          -- 来源: api_test, ui_test, anti_crawl, source_evolution
    source_id VARCHAR(255),                    -- 来源ID
    source_data JSONB DEFAULT '{}',            -- 原始数据

    -- 任务内容
    title VARCHAR(255) NOT NULL,               -- 标题
    description TEXT,                          -- 详细描述

    -- 优先级和分类
    priority INT DEFAULT 2,                     -- 优先级: 0=紧急(P0), 1=重要(P1), 2=普通(P2), 3=建议(P3)
    category VARCHAR(50),                       -- 分类: functional, performance, security, config

    -- 状态
    status VARCHAR(20) DEFAULT 'pending',      -- pending, confirmed, rejected, executing, completed, failed

    -- 处理方式
    auto_processible BOOLEAN DEFAULT FALSE,    -- 是否可自动处理
    auto_process_config JSONB DEFAULT '{}',    -- 自动处理配置

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    executing_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    expired_at TIMESTAMP WITH TIME ZONE,        -- 过期时间（超时后自动拒绝）

    -- 创建者
    created_by VARCHAR(100) DEFAULT 'system'   -- system, ai, user
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_source ON tasks(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_tasks_priority_status ON tasks(priority, status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. 任务处理历史表 (task_history)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS task_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,

    -- 处理信息
    action VARCHAR(50) NOT NULL,               -- auto_retry, manual_confirm, auto_fix, confirm, reject, execute
    result VARCHAR(50) NOT NULL,               -- success, failed, skipped, timeout

    -- 详细信息
    details JSONB DEFAULT '{}',                 -- 详细信息（错误信息、重试次数等）

    -- 执行者
    performed_by VARCHAR(100) DEFAULT 'system', -- system, ai, user

    -- 时间
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_task_history_task ON task_history(task_id, created_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- 3. 系统配置扩展 (system_config)
-- ═══════════════════════════════════════════════════════════════════════════

-- 添加通知渠道配置（如果表存在）
DO $$
BEGIN
    IF to_regclass('public.system_config') IS NOT NULL THEN
        ALTER TABLE system_config ADD COLUMN IF NOT EXISTS notify_channels JSONB DEFAULT '["web"]';
        ALTER TABLE system_config ADD COLUMN IF NOT EXISTS auto_process_p0 BOOLEAN DEFAULT TRUE;
        ALTER TABLE system_config ADD COLUMN IF NOT EXISTS confirm_timeout_minutes INT DEFAULT 60;
    END IF;
END $$;

-- ═══════════════════════════════════════════════════════════════════════════
-- 注释
-- ═══════════════════════════════════════════════════════════════════════════

COMMENT ON TABLE tasks IS '任务表 - 存储系统检测到的问题和待处理任务';
COMMENT ON TABLE task_history IS '任务处理历史 - 记录每个任务的处理过程';
COMMENT ON COLUMN tasks.priority IS '优先级: 0=紧急(P0-自动处理), 1=重要(P1-需确认), 2=普通(P2-汇总), 3=建议(P3-定期)';
COMMENT ON COLUMN tasks.status IS '状态: pending(待处理), confirmed(已确认), rejected(已拒绝), executing(执行中), completed(已完成), failed(失败)';
COMMENT ON COLUMN tasks.auto_processible IS 'P0级别任务可自动处理，如API测试失败自动重试、反爬自动切换策略';
