ALTER TABLE task_history
    ALTER COLUMN task_id DROP NOT NULL;

ALTER TABLE task_artifacts
    ALTER COLUMN task_id DROP NOT NULL;
