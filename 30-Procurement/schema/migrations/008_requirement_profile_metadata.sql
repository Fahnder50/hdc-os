ALTER TABLE requirement_profiles ADD COLUMN version TEXT NOT NULL DEFAULT '1.0';
ALTER TABLE requirement_profiles ADD COLUMN approved_at TEXT;
