CREATE TABLE IF NOT EXISTS content_items (
    id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    block_type TEXT NOT NULL,
    text TEXT NOT NULL,
    scope TEXT NOT NULL,
    topics_json TEXT NOT NULL,
    allowed_signs_json TEXT NOT NULL,
    required_rule_ids_json TEXT NOT NULL,
    forbidden_rule_ids_json TEXT NOT NULL,
    allowed_tones_json TEXT NOT NULL,
    min_gap_days INTEGER NOT NULL CHECK (min_gap_days >= 0),
    review_status TEXT NOT NULL,
    notes TEXT,
    word_count INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    raw_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (id, version)
);
CREATE INDEX IF NOT EXISTS idx_content_selection ON content_items(block_type, review_status, scope);

CREATE TABLE IF NOT EXISTS seed_imports (
    source_name TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    PRIMARY KEY (source_name, schema_version, source_sha256)
);

CREATE TABLE IF NOT EXISTS rule_versions (
    rule_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    definition_json TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (rule_id, version)
);

CREATE TABLE IF NOT EXISTS astronomical_events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    start_utc TEXT NOT NULL,
    exact_time INTEGER NOT NULL,
    planets_json TEXT NOT NULL,
    data_json TEXT NOT NULL,
    eph_version TEXT NOT NULL,
    calculation_parameters_json TEXT NOT NULL,
    algorithm_version TEXT NOT NULL,
    calculation_hash TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_astronomy_start ON astronomical_events(start_utc);

CREATE TABLE IF NOT EXISTS astronomy_days (
    local_date TEXT NOT NULL,
    timezone TEXT NOT NULL,
    eph_version TEXT NOT NULL,
    algorithm_version TEXT NOT NULL,
    parameters_json TEXT NOT NULL,
    snapshot_json TEXT NOT NULL,
    calculated_at TEXT NOT NULL,
    PRIMARY KEY (local_date, eph_version, algorithm_version)
);
CREATE TABLE IF NOT EXISTS astronomy_day_events (
    local_date TEXT NOT NULL,
    eph_version TEXT NOT NULL,
    algorithm_version TEXT NOT NULL,
    event_id TEXT NOT NULL REFERENCES astronomical_events(id) ON DELETE RESTRICT,
    PRIMARY KEY (local_date, eph_version, algorithm_version, event_id),
    FOREIGN KEY (local_date, eph_version, algorithm_version)
      REFERENCES astronomy_days(local_date, eph_version, algorithm_version) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS published_forecasts (
    id TEXT PRIMARY KEY,
    forecast_date TEXT NOT NULL,
    sign TEXT NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1 CHECK (revision > 0),
    status TEXT NOT NULL CHECK (status IN ('published', 'superseded')),
    timezone TEXT NOT NULL,
    created_at TEXT NOT NULL,
    published_at TEXT NOT NULL,
    astronomy_snapshot_json TEXT NOT NULL,
    astrology_context_json TEXT NOT NULL,
    event_ids_json TEXT NOT NULL,
    rule_versions_json TEXT NOT NULL,
    algorithm_version TEXT NOT NULL,
    fallback_reasons_json TEXT NOT NULL,
    export_json TEXT NOT NULL,
    UNIQUE (forecast_date, sign, revision)
);
CREATE INDEX IF NOT EXISTS idx_forecast_export ON published_forecasts(forecast_date, sign, status, revision);

CREATE TABLE IF NOT EXISTS forecast_blocks (
    forecast_id TEXT NOT NULL REFERENCES published_forecasts(id) ON DELETE RESTRICT,
    block_type TEXT NOT NULL,
    content_id TEXT NOT NULL,
    content_version INTEGER NOT NULL,
    fallback_reason TEXT,
    PRIMARY KEY (forecast_id, block_type),
    FOREIGN KEY (content_id, content_version) REFERENCES content_items(id, version) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS content_assignments (
    forecast_date TEXT NOT NULL,
    sign TEXT NOT NULL,
    block_type TEXT NOT NULL,
    revision INTEGER NOT NULL DEFAULT 1,
    content_id TEXT NOT NULL,
    content_version INTEGER NOT NULL,
    forecast_id TEXT REFERENCES published_forecasts(id) ON DELETE RESTRICT,
    selected_at TEXT NOT NULL,
    fallback_reason TEXT,
    UNIQUE (forecast_id, block_type),
    UNIQUE (forecast_date, sign, block_type, revision, content_id, content_version),
    FOREIGN KEY (content_id, content_version) REFERENCES content_items(id, version) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_assignment_rotation ON content_assignments(sign, block_type, forecast_date);
CREATE INDEX IF NOT EXISTS idx_assignment_item_usage ON content_assignments(content_id, content_version, sign, block_type, forecast_date);

CREATE TABLE IF NOT EXISTS algorithm_runs (
    id TEXT PRIMARY KEY,
    command TEXT NOT NULL,
    run_date TEXT,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    diagnostics_json TEXT NOT NULL,
    error TEXT
);
