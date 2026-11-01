-- Run once on an existing Marasses/Supabase database before enabling GeniusPay.
ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_provider VARCHAR(30);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_reference VARCHAR(100);
ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_checkout_url TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_payment_reference ON orders(payment_reference) WHERE payment_reference IS NOT NULL;
ALTER TABLE orders ADD COLUMN IF NOT EXISTS payment_status_token_hash VARCHAR(64);
