CREATE TABLE IF NOT EXISTS support_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference VARCHAR(20) UNIQUE NOT NULL,
    order_number VARCHAR(20),
    customer_phone VARCHAR(20) NOT NULL,
    topic VARCHAR(30) NOT NULL CHECK(topic IN ('Commande','Livraison','Paiement','Produit','Autre')),
    message TEXT NOT NULL CHECK(length(message) BETWEEN 10 AND 2000),
    consent_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_support_requests_created_at ON support_requests(created_at DESC);
