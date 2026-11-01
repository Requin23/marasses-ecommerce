ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS delivery_latitude DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS delivery_longitude DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS delivery_location_accuracy_m DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS delivery_location_consent_at TIMESTAMPTZ;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'orders_delivery_latitude_range'
    ) THEN
        ALTER TABLE orders ADD CONSTRAINT orders_delivery_latitude_range
            CHECK (delivery_latitude IS NULL OR delivery_latitude BETWEEN -90 AND 90);
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'orders_delivery_longitude_range'
    ) THEN
        ALTER TABLE orders ADD CONSTRAINT orders_delivery_longitude_range
            CHECK (delivery_longitude IS NULL OR delivery_longitude BETWEEN -180 AND 180);
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'orders_delivery_accuracy_nonnegative'
    ) THEN
        ALTER TABLE orders ADD CONSTRAINT orders_delivery_accuracy_nonnegative
            CHECK (delivery_location_accuracy_m IS NULL OR delivery_location_accuracy_m >= 0);
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'orders_delivery_location_consent'
    ) THEN
        ALTER TABLE orders ADD CONSTRAINT orders_delivery_location_consent
            CHECK (
                (delivery_latitude IS NULL AND delivery_longitude IS NULL AND delivery_location_consent_at IS NULL)
                OR
                (delivery_latitude IS NOT NULL AND delivery_longitude IS NOT NULL AND delivery_location_consent_at IS NOT NULL)
            );
    END IF;
END $$;
