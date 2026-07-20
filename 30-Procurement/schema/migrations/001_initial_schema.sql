CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS runtime_metadata (
    metadata_key TEXT PRIMARY KEY,
    metadata_value TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS procurement_cases (
    id INTEGER PRIMARY KEY,
    case_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    priority TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS requirements (
    id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES procurement_cases(id) ON DELETE CASCADE,
    requirement_id TEXT NOT NULL,
    name TEXT NOT NULL,
    value_json TEXT,
    status TEXT NOT NULL DEFAULT 'UNKNOWN',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(case_id, requirement_id)
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    product_id TEXT NOT NULL UNIQUE,
    manufacturer TEXT,
    model TEXT,
    product_name TEXT NOT NULL,
    technical_reference TEXT,
    status TEXT NOT NULL DEFAULT 'candidate',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS case_products (
    case_id INTEGER NOT NULL REFERENCES procurement_cases(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'proposed',
    created_at TEXT NOT NULL,
    PRIMARY KEY(case_id, product_id)
);

CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY,
    vendor_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'known',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS offers (
    id INTEGER PRIMARY KEY,
    offer_id TEXT NOT NULL UNIQUE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    vendor_id INTEGER NOT NULL REFERENCES vendors(id) ON DELETE RESTRICT,
    source_type TEXT NOT NULL,
    source_reference TEXT,
    price_cents INTEGER,
    shipping_cents INTEGER,
    total_price_cents INTEGER,
    currency TEXT NOT NULL,
    availability TEXT,
    delivery_note TEXT,
    observed_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS price_observations (
    id INTEGER PRIMARY KEY,
    observation_id TEXT NOT NULL UNIQUE,
    offer_id INTEGER NOT NULL REFERENCES offers(id) ON DELETE CASCADE,
    price_cents INTEGER,
    shipping_cents INTEGER,
    total_price_cents INTEGER,
    currency TEXT NOT NULL,
    availability TEXT,
    observed_at TEXT NOT NULL,
    source_adapter TEXT NOT NULL,
    watch_run_id INTEGER REFERENCES watch_runs(id) ON DELETE SET NULL,
    validation_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY,
    evaluation_id TEXT NOT NULL UNIQUE,
    case_id INTEGER NOT NULL REFERENCES procurement_cases(id) ON DELETE CASCADE,
    requirement_id INTEGER REFERENCES requirements(id) ON DELETE SET NULL,
    offer_id INTEGER REFERENCES offers(id) ON DELETE SET NULL,
    watch_run_id INTEGER REFERENCES watch_runs(id) ON DELETE SET NULL,
    result TEXT NOT NULL,
    reason TEXT,
    evaluated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS watch_runs (
    id INTEGER PRIMARY KEY,
    watch_run_id TEXT NOT NULL UNIQUE,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT NOT NULL,
    error_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS watch_run_results (
    id INTEGER PRIMARY KEY,
    watch_run_id INTEGER NOT NULL REFERENCES watch_runs(id) ON DELETE CASCADE,
    case_id INTEGER REFERENCES procurement_cases(id) ON DELETE SET NULL,
    source_id TEXT,
    status TEXT NOT NULL,
    message TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    case_id INTEGER REFERENCES procurement_cases(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    deduplication_key TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'open',
    message TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT
);

CREATE TABLE IF NOT EXISTS purchase_decisions (
    id INTEGER PRIMARY KEY,
    decision_id TEXT NOT NULL UNIQUE,
    case_id INTEGER NOT NULL REFERENCES procurement_cases(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    decided_by TEXT,
    reason TEXT,
    decided_at TEXT
);

CREATE TABLE IF NOT EXISTS asset_handovers (
    id INTEGER PRIMARY KEY,
    handover_id TEXT NOT NULL UNIQUE,
    case_id INTEGER NOT NULL REFERENCES procurement_cases(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    purchase_decision_id INTEGER REFERENCES purchase_decisions(id) ON DELETE SET NULL,
    status TEXT NOT NULL,
    handed_over_at TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_requirements_case ON requirements(case_id);
CREATE INDEX IF NOT EXISTS idx_offers_product ON offers(product_id);
CREATE INDEX IF NOT EXISTS idx_observations_offer ON price_observations(offer_id, observed_at);
CREATE INDEX IF NOT EXISTS idx_watch_runs_started ON watch_runs(started_at);
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status, created_at);
