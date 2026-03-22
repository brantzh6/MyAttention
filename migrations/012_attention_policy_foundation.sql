CREATE TABLE IF NOT EXISTS attention_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    focus VARCHAR(50) NOT NULL DEFAULT 'authoritative',
    description TEXT,
    problem_type VARCHAR(100) DEFAULT 'source_intelligence',
    thinking_framework VARCHAR(100) DEFAULT 'attention_model',
    candidate_mix_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    scoring_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    gate_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    execution_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    current_version INTEGER NOT NULL DEFAULT 1,
    latest_version INTEGER NOT NULL DEFAULT 1,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS attention_policy_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id_ref UUID NOT NULL REFERENCES attention_policies(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    parent_version INTEGER,
    change_reason TEXT,
    candidate_mix_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    scoring_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    gate_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    execution_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    decision_status VARCHAR(20) NOT NULL DEFAULT 'accepted',
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    accepted_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_attention_policy_versions_policy_version
    ON attention_policy_versions(policy_id_ref, version_number);

CREATE INDEX IF NOT EXISTS idx_attention_policies_focus_status
    ON attention_policies(focus, status);

CREATE INDEX IF NOT EXISTS idx_attention_policy_versions_policy_created
    ON attention_policy_versions(policy_id_ref, created_at DESC);
