CREATE TABLE IF NOT EXISTS journal_entries (
    id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES procurement_cases(id) ON DELETE CASCADE,
    watch_run_id INTEGER REFERENCES watch_runs(id) ON DELETE SET NULL,
    entry_id TEXT NOT NULL UNIQUE,
    observed_at TEXT NOT NULL,
    recommendation_status TEXT NOT NULL,
    summary_json TEXT NOT NULL,
    changes_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_journal_case_observed ON journal_entries(case_id, observed_at);
