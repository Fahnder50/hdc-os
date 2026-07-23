ALTER TABLE products ADD COLUMN technical_json TEXT;
ALTER TABLE evaluations ADD COLUMN rule_id TEXT;

CREATE TRIGGER IF NOT EXISTS prevent_price_observations_update
BEFORE UPDATE ON price_observations
BEGIN
    SELECT RAISE(ABORT, 'price_observations are immutable; insert a new observation');
END;

CREATE TRIGGER IF NOT EXISTS prevent_price_observations_delete
BEFORE DELETE ON price_observations
BEGIN
    SELECT RAISE(ABORT, 'price_observations are immutable; insert a new observation');
END;
