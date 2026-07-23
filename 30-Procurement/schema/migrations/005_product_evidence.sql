ALTER TABLE products ADD COLUMN model_number TEXT;
ALTER TABLE products ADD COLUMN ean TEXT;
ALTER TABLE products ADD COLUMN region_variant TEXT;
ALTER TABLE products ADD COLUMN outlet_type TEXT NOT NULL DEFAULT 'unknown';
ALTER TABLE products ADD COLUMN evidence_status TEXT NOT NULL DEFAULT 'unknown';
ALTER TABLE products ADD COLUMN evidence_json TEXT NOT NULL DEFAULT '{}';
ALTER TABLE price_observations ADD COLUMN product_evidence_json TEXT NOT NULL DEFAULT '{}';

CREATE UNIQUE INDEX IF NOT EXISTS idx_products_model_variant ON products(model_number, region_variant);
