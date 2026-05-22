-- Migration: 013_runtime_v0_kernel_foundation
-- IKE Runtime v0 – Core schema foundation (Slice A+B+C)
-- Purpose: Create the first canonical runtime tables for durable kernel state.
-- Scope: schema only – no APIs, no UI, no retrieval.

BEGIN;

-- ─── ENUM TYPES ───────────────────────────────────────────────────────────────

CREATE TYPE runtime_task_status AS ENUM (
    'inbox', 'ready', 'active', 'waiting',
    'review_pending', 'done', 'failed'
);

CREATE TYPE runtime_project_status AS ENUM (
    'active', 'paused', 'blocked', 'completed', 'archived'
);

CREATE TYPE runtime_task_type AS ENUM (
    'inbox', 'study', 'implementation', 'review',
    'maintenance', 'workflow', 'daemon'
);

CREATE TYPE runtime_owner_kind AS ENUM (
    'controller', 'delegate', 'runtime', 'scheduler', 'reviewer', 'user'
);

CREATE TYPE runtime_review_status AS ENUM (
    'pending', 'accepted', 'rejected', 'needs_revision'
);

CREATE TYPE runtime_decision_outcome AS ENUM (
    'adopt', 'reject', 'defer', 'escalate'
);

CREATE TYPE runtime_decision_status AS ENUM (
    'draft', 'review_pending', 'final', 'superseded'
);

CREATE TYPE runtime_packet_status AS ENUM (
    'draft', 'pending_review', 'accepted'
);

CREATE TYPE runtime_lease_status AS ENUM (
    'active', 'expired', 'released'
);

CREATE TYPE runtime_context_status AS ENUM (
    'active', 'archived'
);

CREATE TYPE runtime_outbox_publish_status AS ENUM (
    'pending', 'published', 'failed'
);

-- ─── TABLES ───────────────────────────────────────────────────────────────────

CREATE TABLE runtime_projects (
    project_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_key       VARCHAR(100) NOT NULL UNIQUE,
    title             VARCHAR(500) NOT NULL,
    goal              TEXT,
    status            runtime_project_status NOT NULL DEFAULT 'active',
    current_phase     VARCHAR(100),
    priority          INTEGER NOT NULL DEFAULT 2,
    owner_type        VARCHAR(50),
    owner_id          VARCHAR(255),
    current_work_context_id UUID,  -- FK added after runtime_work_contexts exists
    blocker_summary   TEXT,
    next_milestone    VARCHAR(500),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at         TIMESTAMPTZ,
    metadata          JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE runtime_tasks (
    task_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id           UUID NOT NULL REFERENCES runtime_projects(project_id) ON DELETE CASCADE,
    task_type            runtime_task_type NOT NULL,
    title                VARCHAR(500) NOT NULL,
    goal                 TEXT,
    status               runtime_task_status NOT NULL DEFAULT 'inbox',
    priority             INTEGER NOT NULL DEFAULT 2,
    owner_kind           runtime_owner_kind,
    owner_id             VARCHAR(255),
    parent_task_id       UUID REFERENCES runtime_tasks(task_id) ON DELETE SET NULL,
    decision_id          UUID,  -- FK added after runtime_decisions exists
    active_checkpoint_id UUID,  -- FK added after runtime_task_checkpoints exists
    current_lease_id     UUID,  -- FK added after runtime_worker_leases exists
    review_required      BOOLEAN NOT NULL DEFAULT false,
    review_status        runtime_review_status,
    waiting_reason       VARCHAR(100),
    waiting_detail       TEXT,
    lease_expiry_policy  VARCHAR(100),
    next_action_summary  TEXT,
    result_summary       TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at           TIMESTAMPTZ,
    ended_at             TIMESTAMPTZ,
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata             JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE runtime_decisions (
    decision_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id               UUID NOT NULL REFERENCES runtime_projects(project_id) ON DELETE CASCADE,
    task_id                  UUID REFERENCES runtime_tasks(task_id) ON DELETE SET NULL,
    decision_scope           VARCHAR(100) NOT NULL,
    title                    VARCHAR(500) NOT NULL,
    summary                  TEXT,
    rationale                TEXT,
    outcome                  runtime_decision_outcome,
    status                   runtime_decision_status NOT NULL DEFAULT 'draft',
    impact_scope             VARCHAR(200),
    supersedes_decision_id   UUID REFERENCES runtime_decisions(decision_id) ON DELETE SET NULL,
    created_by_kind          runtime_owner_kind NOT NULL,
    created_by_id            VARCHAR(255),
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    finalized_at             TIMESTAMPTZ,
    metadata                 JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE runtime_task_events (
    event_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id         UUID NOT NULL REFERENCES runtime_projects(project_id) ON DELETE CASCADE,
    task_id            UUID NOT NULL REFERENCES runtime_tasks(task_id) ON DELETE CASCADE,
    event_type         VARCHAR(100) NOT NULL,
    from_status        runtime_task_status,
    to_status          runtime_task_status,
    triggered_by_kind  runtime_owner_kind NOT NULL,
    triggered_by_id    VARCHAR(255),
    reason             TEXT,
    payload            JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE runtime_worker_leases (
    lease_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id        UUID NOT NULL REFERENCES runtime_tasks(task_id) ON DELETE CASCADE,
    owner_kind     runtime_owner_kind NOT NULL,
    owner_id       VARCHAR(255),
    lease_status   runtime_lease_status NOT NULL DEFAULT 'active',
    heartbeat_at   TIMESTAMPTZ,
    expires_at     TIMESTAMPTZ NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata       JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE runtime_work_contexts (
    work_context_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id           UUID NOT NULL REFERENCES runtime_projects(project_id) ON DELETE CASCADE,
    status               runtime_context_status NOT NULL DEFAULT 'active',
    active_task_id       UUID REFERENCES runtime_tasks(task_id) ON DELETE SET NULL,
    latest_decision_id   UUID REFERENCES runtime_decisions(decision_id) ON DELETE SET NULL,
    current_focus        TEXT,
    blockers_summary     TEXT,
    next_steps_summary   TEXT,
    packet_ref_id        UUID,
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata             JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE runtime_memory_packets (
    memory_packet_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id        UUID NOT NULL REFERENCES runtime_projects(project_id) ON DELETE CASCADE,
    task_id           UUID REFERENCES runtime_tasks(task_id) ON DELETE SET NULL,
    packet_type       VARCHAR(100) NOT NULL,
    status            runtime_packet_status NOT NULL DEFAULT 'draft',
    acceptance_trigger VARCHAR(200),
    title             VARCHAR(500) NOT NULL,
    summary           TEXT,
    storage_ref       VARCHAR(500),
    content_hash      VARCHAR(128),
    parent_packet_id  UUID REFERENCES runtime_memory_packets(memory_packet_id) ON DELETE SET NULL,
    created_by_kind   runtime_owner_kind NOT NULL,
    created_by_id     VARCHAR(255),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    accepted_at       TIMESTAMPTZ,
    metadata          JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE runtime_task_checkpoints (
    checkpoint_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id         UUID NOT NULL REFERENCES runtime_tasks(task_id) ON DELETE CASCADE,
    checkpoint_type VARCHAR(100) NOT NULL,
    step_label      VARCHAR(200),
    summary         TEXT,
    storage_ref     VARCHAR(500),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE runtime_outbox_events (
    outbox_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type   VARCHAR(100) NOT NULL,
    aggregate_id     VARCHAR(255) NOT NULL,
    event_type       VARCHAR(100) NOT NULL,
    payload          JSONB NOT NULL DEFAULT '{}'::jsonb,
    publish_status   runtime_outbox_publish_status NOT NULL DEFAULT 'pending',
    attempt_count    INTEGER NOT NULL DEFAULT 0,
    last_attempt_at  TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ─── POST-CREATE FOREIGN KEYS ─────────────────────────────────────────────────

ALTER TABLE runtime_projects
    ADD CONSTRAINT fk_project_work_context
    FOREIGN KEY (current_work_context_id)
    REFERENCES runtime_work_contexts(work_context_id) ON DELETE SET NULL;

ALTER TABLE runtime_tasks
    ADD CONSTRAINT fk_task_decision
    FOREIGN KEY (decision_id)
    REFERENCES runtime_decisions(decision_id) ON DELETE SET NULL;

ALTER TABLE runtime_tasks
    ADD CONSTRAINT fk_task_checkpoint
    FOREIGN KEY (active_checkpoint_id)
    REFERENCES runtime_task_checkpoints(checkpoint_id) ON DELETE SET NULL;

ALTER TABLE runtime_tasks
    ADD CONSTRAINT fk_task_lease
    FOREIGN KEY (current_lease_id)
    REFERENCES runtime_worker_leases(lease_id) ON DELETE SET NULL;

-- ─── INDEXES ──────────────────────────────────────────────────────────────────

-- runtime_projects
CREATE INDEX idx_runtime_projects_status ON runtime_projects(status);
CREATE INDEX idx_runtime_projects_updated_at ON runtime_projects(updated_at DESC);

-- runtime_tasks
CREATE INDEX idx_runtime_tasks_project_status ON runtime_tasks(project_id, status);
CREATE INDEX idx_runtime_tasks_status_priority ON runtime_tasks(status, priority);
CREATE INDEX idx_runtime_tasks_owner ON runtime_tasks(owner_kind, owner_id);
CREATE INDEX idx_runtime_tasks_parent ON runtime_tasks(parent_task_id);
CREATE INDEX idx_runtime_tasks_updated_at ON runtime_tasks(updated_at DESC);

-- runtime_decisions
CREATE INDEX idx_runtime_decisions_project_status ON runtime_decisions(project_id, status);
CREATE INDEX idx_runtime_decisions_task ON runtime_decisions(task_id);
CREATE INDEX idx_runtime_decisions_outcome ON runtime_decisions(outcome);
CREATE INDEX idx_runtime_decisions_finalized ON runtime_decisions(finalized_at);

-- runtime_task_events (append-only – reads are time-ordered)
CREATE INDEX idx_runtime_task_events_task ON runtime_task_events(task_id, created_at);
CREATE INDEX idx_runtime_task_events_project ON runtime_task_events(project_id, created_at);

-- runtime_worker_leases
CREATE INDEX idx_runtime_worker_leases_task ON runtime_worker_leases(task_id);
CREATE INDEX idx_runtime_worker_leases_status ON runtime_worker_leases(lease_status);
CREATE INDEX idx_runtime_worker_leases_expires ON runtime_worker_leases(expires_at);
-- Only one active lease per task
CREATE UNIQUE INDEX idx_runtime_worker_leases_unique_active
    ON runtime_worker_leases(task_id)
    WHERE lease_status = 'active';

-- runtime_work_contexts
CREATE INDEX idx_runtime_work_contexts_project ON runtime_work_contexts(project_id);
CREATE INDEX idx_runtime_work_contexts_status ON runtime_work_contexts(status);
-- One active work context per project
CREATE UNIQUE INDEX idx_runtime_work_contexts_unique_active
    ON runtime_work_contexts(project_id)
    WHERE status = 'active';

-- runtime_memory_packets
CREATE INDEX idx_runtime_memory_packets_project ON runtime_memory_packets(project_id);
CREATE INDEX idx_runtime_memory_packets_task ON runtime_memory_packets(task_id);
CREATE INDEX idx_runtime_memory_packets_status ON runtime_memory_packets(status);
CREATE INDEX idx_runtime_memory_packets_accepted ON runtime_memory_packets(accepted_at);

-- runtime_task_checkpoints
CREATE INDEX idx_runtime_task_checkpoints_task ON runtime_task_checkpoints(task_id, created_at DESC);

-- runtime_outbox_events
CREATE INDEX idx_runtime_outbox_events_status ON runtime_outbox_events(publish_status, created_at);

-- ─── CHECK CONSTRAINTS (explicit, non-JSONB state discipline) ─────────────────

-- waiting_reason must be set when status = 'waiting'
ALTER TABLE runtime_tasks ADD CONSTRAINT chk_waiting_reason
    CHECK (
        status != 'waiting'
        OR (waiting_reason IS NOT NULL AND waiting_reason != '')
    );

-- result_summary expected when task reaches terminal state
ALTER TABLE runtime_tasks ADD CONSTRAINT chk_result_summary_done
    CHECK (
        status != 'done'
        OR result_summary IS NOT NULL
    );

-- heartbeat must be set for active leases
ALTER TABLE runtime_worker_leases ADD CONSTRAINT chk_lease_heartbeat
    CHECK (
        lease_status != 'active'
        OR heartbeat_at IS NOT NULL
    );

COMMIT;

-- ─── ROLLBACK (run manually if needed) ────────────────────────────────────────
-- BEGIN;
-- DROP TABLE IF EXISTS runtime_outbox_events CASCADE;
-- DROP TABLE IF EXISTS runtime_task_checkpoints CASCADE;
-- DROP TABLE IF EXISTS runtime_memory_packets CASCADE;
-- DROP TABLE IF EXISTS runtime_work_contexts CASCADE;
-- DROP TABLE IF EXISTS runtime_worker_leases CASCADE;
-- DROP TABLE IF EXISTS runtime_task_events CASCADE;
-- DROP TABLE IF EXISTS runtime_decisions CASCADE;
-- DROP TABLE IF EXISTS runtime_tasks CASCADE;
-- DROP TABLE IF EXISTS runtime_projects CASCADE;
-- DROP TYPE IF EXISTS runtime_outbox_publish_status CASCADE;
-- DROP TYPE IF EXISTS runtime_context_status CASCADE;
-- DROP TYPE IF EXISTS runtime_packet_status CASCADE;
-- DROP TYPE IF EXISTS runtime_lease_status CASCADE;
-- DROP TYPE IF EXISTS runtime_decision_status CASCADE;
-- DROP TYPE IF EXISTS runtime_decision_outcome CASCADE;
-- DROP TYPE IF EXISTS runtime_review_status CASCADE;
-- DROP TYPE IF EXISTS runtime_owner_kind CASCADE;
-- DROP TYPE IF EXISTS runtime_task_type CASCADE;
-- DROP TYPE IF EXISTS runtime_project_status CASCADE;
-- DROP TYPE IF EXISTS runtime_task_status CASCADE;
-- COMMIT;
