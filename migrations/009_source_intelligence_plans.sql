CREATE TABLE IF NOT EXISTS source_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic VARCHAR(255) NOT NULL,
    focus VARCHAR(50) NOT NULL DEFAULT 'authoritative',
    objective TEXT,
    owner_type VARCHAR(50) DEFAULT 'system',
    owner_id VARCHAR(255),
    planning_brain VARCHAR(100) DEFAULT 'source-intelligence-brain',
    status VARCHAR(20) DEFAULT 'active',
    review_status VARCHAR(20) DEFAULT 'pending',
    review_cadence_days INTEGER DEFAULT 14,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_source_plans_topic ON source_plans(topic);
CREATE INDEX IF NOT EXISTS idx_source_plans_status ON source_plans(status);
CREATE INDEX IF NOT EXISTS idx_source_plans_focus ON source_plans(focus);

CREATE TABLE IF NOT EXISTS source_plan_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES source_plans(id) ON DELETE CASCADE,
    item_type VARCHAR(50) DEFAULT 'domain',
    object_key VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    url TEXT,
    authority_tier VARCHAR(10),
    authority_score DOUBLE PRECISION DEFAULT 0.0,
    monitoring_mode VARCHAR(50) DEFAULT 'review',
    execution_strategy VARCHAR(50) DEFAULT 'search_review',
    review_cadence_days INTEGER DEFAULT 14,
    rationale TEXT,
    evidence JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_source_plan_items_plan_id ON source_plan_items(plan_id);
CREATE INDEX IF NOT EXISTS idx_source_plan_items_object_key ON source_plan_items(object_key);
CREATE INDEX IF NOT EXISTS idx_source_plan_items_status ON source_plan_items(status);
