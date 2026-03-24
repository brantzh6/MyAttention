-- Task and brain foundation migration
-- Adds V1 task workflow foundation and brain control plane tables

-- Extend existing tasks table for V1 workflow semantics
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS context_id UUID;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS task_type VARCHAR(50) DEFAULT 'workflow';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS goal TEXT;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS parent_task_id UUID;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS initiator_type VARCHAR(50);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS initiator_id VARCHAR(255);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS assigned_brain VARCHAR(100);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS assigned_agent VARCHAR(100);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS budget_policy JSONB DEFAULT '{}';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS timeout_policy JSONB DEFAULT '{}';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS retry_policy JSONB DEFAULT '{}';
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS checkpoint_ref VARCHAR(255);
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS result_summary TEXT;

-- Long-lived contexts
CREATE TABLE IF NOT EXISTS task_contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    context_type VARCHAR(50) NOT NULL DEFAULT 'system',
    title VARCHAR(255) NOT NULL,
    goal TEXT,
    owner_type VARCHAR(50),
    owner_id VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    priority INT DEFAULT 2,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE
);

ALTER TABLE tasks
    ADD CONSTRAINT fk_tasks_context_id
    FOREIGN KEY (context_id) REFERENCES task_contexts(id) ON DELETE SET NULL;

ALTER TABLE tasks
    ADD CONSTRAINT fk_tasks_parent_task_id
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE SET NULL;

-- Extend task history into event history compatible shape
ALTER TABLE task_history ADD COLUMN IF NOT EXISTS context_id UUID;
ALTER TABLE task_history ADD COLUMN IF NOT EXISTS event_type VARCHAR(50);
ALTER TABLE task_history ADD COLUMN IF NOT EXISTS from_status VARCHAR(20);
ALTER TABLE task_history ADD COLUMN IF NOT EXISTS to_status VARCHAR(20);
ALTER TABLE task_history ADD COLUMN IF NOT EXISTS reason TEXT;
ALTER TABLE task_history ADD COLUMN IF NOT EXISTS payload JSONB DEFAULT '{}';

ALTER TABLE task_history
    ADD CONSTRAINT fk_task_history_context_id
    FOREIGN KEY (context_id) REFERENCES task_contexts(id) ON DELETE SET NULL;

-- Structured artifacts
CREATE TABLE IF NOT EXISTS task_artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    context_id UUID NOT NULL REFERENCES task_contexts(id) ON DELETE CASCADE,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    artifact_type VARCHAR(50) NOT NULL,
    version INT DEFAULT 1,
    parent_version INT,
    title VARCHAR(255) NOT NULL,
    summary TEXT,
    storage_ref TEXT,
    content_ref TEXT,
    created_by VARCHAR(100) DEFAULT 'system',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Relations across contexts, tasks, and artifacts
CREATE TABLE IF NOT EXISTS task_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(255) NOT NULL,
    relation_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    target_id VARCHAR(255) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Brain control plane foundation
CREATE TABLE IF NOT EXISTS brain_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brain_id VARCHAR(100) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL,
    description TEXT,
    capabilities TEXT[] DEFAULT ARRAY[]::TEXT[],
    default_models JSONB DEFAULT '[]',
    fallback_models JSONB DEFAULT '[]',
    tool_policy JSONB DEFAULT '{}',
    cost_policy JSONB DEFAULT '{}',
    latency_policy JSONB DEFAULT '{}',
    risk_policy JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active',
    version INT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS brain_routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id VARCHAR(100) NOT NULL UNIQUE,
    problem_type VARCHAR(100) NOT NULL,
    thinking_framework VARCHAR(100),
    primary_brain_id UUID NOT NULL REFERENCES brain_profiles(id) ON DELETE CASCADE,
    supporting_brains TEXT[] DEFAULT ARRAY[]::TEXT[],
    review_brain_id UUID REFERENCES brain_profiles(id) ON DELETE SET NULL,
    fallback_brain_id UUID REFERENCES brain_profiles(id) ON DELETE SET NULL,
    version INT DEFAULT 1,
    enabled BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS brain_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id VARCHAR(100) NOT NULL UNIQUE,
    brain_id VARCHAR(100),
    route_id VARCHAR(100),
    cost_policy JSONB DEFAULT '{}',
    latency_policy JSONB DEFAULT '{}',
    execution_policy JSONB DEFAULT '{}',
    network_policy JSONB DEFAULT '{}',
    timeout_policy JSONB DEFAULT '{}',
    degrade_policy JSONB DEFAULT '{}',
    enabled BOOLEAN DEFAULT TRUE,
    version INT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS brain_fallbacks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fallback_id VARCHAR(100) NOT NULL UNIQUE,
    brain_id VARCHAR(100) NOT NULL,
    failure_mode VARCHAR(100) NOT NULL,
    fallback_brain VARCHAR(100),
    fallback_mode VARCHAR(100) DEFAULT 'degrade',
    fallback_policy JSONB DEFAULT '{}',
    enabled BOOLEAN DEFAULT TRUE,
    version INT DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_task_contexts_type_status ON task_contexts(context_type, status);
CREATE INDEX IF NOT EXISTS idx_tasks_context_id ON tasks(context_id);
CREATE INDEX IF NOT EXISTS idx_tasks_parent_task_id ON tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_task_type_status ON tasks(task_type, status);
CREATE INDEX IF NOT EXISTS idx_task_history_context_id ON task_history(context_id);
CREATE INDEX IF NOT EXISTS idx_task_history_event_type ON task_history(event_type);
CREATE INDEX IF NOT EXISTS idx_task_artifacts_task_id ON task_artifacts(task_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_task_artifacts_context_id ON task_artifacts(context_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_task_relations_source ON task_relations(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_task_relations_target ON task_relations(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_brain_profiles_role_status ON brain_profiles(role, status);
CREATE INDEX IF NOT EXISTS idx_brain_routes_problem_type ON brain_routes(problem_type);
CREATE INDEX IF NOT EXISTS idx_brain_routes_primary ON brain_routes(primary_brain_id);
