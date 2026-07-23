ALTER TABLE offers ADD COLUMN product_url TEXT;
ALTER TABLE offers ADD COLUMN delivery_text_raw TEXT;
ALTER TABLE offers ADD COLUMN delivery_date_earliest TEXT;
ALTER TABLE offers ADD COLUMN delivery_date_latest TEXT;
ALTER TABLE offers ADD COLUMN delivery_confidence TEXT NOT NULL DEFAULT 'unknown';
ALTER TABLE offers ADD COLUMN delivery_eligibility TEXT NOT NULL DEFAULT 'unknown';
ALTER TABLE offers ADD COLUMN fulfillment_type TEXT NOT NULL DEFAULT 'unknown';
ALTER TABLE offers ADD COLUMN pickup_location TEXT;

ALTER TABLE price_observations ADD COLUMN delivery_text_raw TEXT;
ALTER TABLE price_observations ADD COLUMN delivery_date_earliest TEXT;
ALTER TABLE price_observations ADD COLUMN delivery_date_latest TEXT;
ALTER TABLE price_observations ADD COLUMN delivery_confidence TEXT NOT NULL DEFAULT 'unknown';
ALTER TABLE price_observations ADD COLUMN delivery_eligibility TEXT NOT NULL DEFAULT 'unknown';
ALTER TABLE price_observations ADD COLUMN fulfillment_type TEXT NOT NULL DEFAULT 'unknown';
ALTER TABLE price_observations ADD COLUMN pickup_location TEXT;
ALTER TABLE price_observations ADD COLUMN product_url TEXT;

ALTER TABLE watch_run_results ADD COLUMN records_processed INTEGER NOT NULL DEFAULT 0;
ALTER TABLE watch_run_results ADD COLUMN error_class TEXT;

CREATE INDEX IF NOT EXISTS idx_offers_delivery ON offers(delivery_eligibility, delivery_date_latest);
