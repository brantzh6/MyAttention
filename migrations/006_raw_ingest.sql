-- Raw ingest metadata for object-store-backed feed imports

CREATE TABLE IF NOT EXISTS raw_ingest (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_key VARCHAR(255) NOT NULL,
    external_id VARCHAR(512),
    object_key TEXT NOT NULL UNIQUE,
    storage_backend VARCHAR(50) NOT NULL DEFAULT 'local',
    content_type VARCHAR(255),
    content_encoding VARCHAR(100),
    content_hash VARCHAR(128) NOT NULL,
    size_bytes INTEGER NOT NULL DEFAULT 0,
    fetched_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    http_status INTEGER,
    access_method VARCHAR(50),
    proxy_used BOOLEAN DEFAULT false,
    anti_crawl_status VARCHAR(50),
    request_meta JSONB DEFAULT '{}',
    response_meta JSONB DEFAULT '{}',
    parse_status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_raw_ingest_source_external
    ON raw_ingest (source_key, external_id)
    WHERE external_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_raw_ingest_source_key ON raw_ingest(source_key);
CREATE INDEX IF NOT EXISTS idx_raw_ingest_fetched_at ON raw_ingest(fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_raw_ingest_content_hash ON raw_ingest(content_hash);
