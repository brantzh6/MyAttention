ALTER TABLE source_plans
    ADD COLUMN IF NOT EXISTS current_version INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS latest_version INTEGER NOT NULL DEFAULT 1;

CREATE TABLE IF NOT EXISTS source_plan_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES source_plans(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    parent_version INTEGER,
    trigger_type VARCHAR(50) NOT NULL DEFAULT 'manual_refresh',
    decision_status VARCHAR(20) NOT NULL DEFAULT 'accepted',
    change_reason TEXT,
    change_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    plan_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    evaluation JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    accepted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_source_plan_versions_plan_version
    ON source_plan_versions(plan_id, version_number);

CREATE INDEX IF NOT EXISTS idx_source_plan_versions_plan_created
    ON source_plan_versions(plan_id, created_at DESC);
