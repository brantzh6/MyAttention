CREATE TABLE IF NOT EXISTS task_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    context_id UUID NOT NULL REFERENCES task_contexts(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    memory_kind VARCHAR(50) NOT NULL DEFAULT 'checkpoint',
    title VARCHAR(255) NOT NULL,
    summary TEXT,
    content TEXT,
    created_by VARCHAR(100) DEFAULT 'system',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_task_memories_context_id ON task_memories(context_id);
CREATE INDEX IF NOT EXISTS idx_task_memories_task_id ON task_memories(task_id);
CREATE INDEX IF NOT EXISTS idx_task_memories_kind ON task_memories(memory_kind);

CREATE TABLE IF NOT EXISTS procedural_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_key VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    problem_type VARCHAR(100),
    thinking_framework VARCHAR(100),
    method_name VARCHAR(100),
    applicability TEXT,
    procedure TEXT,
    effectiveness_score DOUBLE PRECISION DEFAULT 0.0,
    validation_status VARCHAR(20) DEFAULT 'draft',
    source_kind VARCHAR(50) DEFAULT 'system',
    source_ref VARCHAR(255),
    version INTEGER DEFAULT 1,
    parent_version INTEGER,
    last_validated_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_procedural_memories_problem_type ON procedural_memories(problem_type);
CREATE INDEX IF NOT EXISTS idx_procedural_memories_validation_status ON procedural_memories(validation_status);
