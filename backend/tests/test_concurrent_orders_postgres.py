"""PostgreSQL integration test; requires a disposable local database named marasses_test."""

import os
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from starlette.testclient import TestClient

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "").strip()

if TEST_DATABASE_URL:
    test_url = make_url(TEST_DATABASE_URL)
    if test_url.host not in {"localhost", "127.0.0.1", "::1"} or test_url.database != "marasses_test":
        raise RuntimeError("TEST_DATABASE_URL must point to localhost database named marasses_test; production databases are refused.")
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.main import _rate_limit_events, _rate_limit_lock, app, engine, rate_limit  # noqa: E402


@unittest.skipUnless(TEST_DATABASE_URL, "Set TEST_DATABASE_URL to a disposable local marasses_test PostgreSQL database.")
class ConcurrentOrderPostgresTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = engine
        cls.schema_file = Path(__file__).resolve().parents[2] / "database" / "schema.sql"
        cls.zone_id = None
        cls.variant_id = None

        # This test is guarded above to a local database with the exact test name.
        with cls.engine.begin() as connection:
            connection.exec_driver_sql("DROP SCHEMA public CASCADE")
            connection.exec_driver_sql("CREATE SCHEMA public")
            for statement in cls.schema_file.read_text(encoding="utf-8").split(";"):
                if statement.strip():
                    connection.exec_driver_sql(statement)
            cls.zone_id = connection.execute(text("""
                INSERT INTO delivery_zones (name, neighborhoods, fee, estimated_delay)
                VALUES ('Test zone', 'Local integration test', 1000, '24h') RETURNING id
            """)).scalar_one()
            product_id = connection.execute(text("""
                INSERT INTO products (name, slug, description)
                VALUES ('Test product', 'integration-test-product', 'Test only') RETURNING id
            """)).scalar_one()
            cls.variant_id = connection.execute(text("""
                INSERT INTO product_variants (product_id, sku, variant_name, price, stock_quantity)
                VALUES (:product_id, 'TEST-RACE', 'Test variant', 500, 3) RETURNING id
            """), {"product_id": product_id}).scalar_one()

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def test_simultaneous_orders_never_sell_more_than_available_stock(self):
        request_bucket = ("orders", "testclient")
        with _rate_limit_lock:
            _rate_limit_events.pop(request_bucket, None)

        start = threading.Barrier(8)
        payload = {
            "delivery_zone_id": str(self.zone_id),
            "customer_phone": "+22670000000",
            "delivery_address": "Local test address",
            "payment_method": "Paiement à la livraison",
            "items": [{"variant_id": str(self.variant_id), "quantity": 1}],
        }

        def submit_order(_):
            with TestClient(app) as client:
                start.wait(timeout=10)
                response = client.post("/api/orders", json=payload)
                return response.status_code, response.json()

        try:
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(submit_order, range(8)))

            statuses = [status for status, _ in results]
            self.assertEqual(statuses.count(201), 3, results)
            self.assertEqual(statuses.count(409), 5, results)
            self.assertTrue(all(status in {201, 409} for status in statuses), results)

            with self.engine.connect() as connection:
                remaining_stock = connection.execute(text(
                    "SELECT stock_quantity FROM product_variants WHERE id=:id"
                ), {"id": self.variant_id}).scalar_one()
                order_count = connection.execute(text(
                    "SELECT count(*) FROM orders"
                )).scalar_one()
                ordered_quantity = connection.execute(text(
                    "SELECT COALESCE(sum(quantity), 0) FROM order_items"
                )).scalar_one()

            self.assertEqual(remaining_stock, 0)
            self.assertEqual(order_count, 3)
            self.assertEqual(ordered_quantity, 3)
        finally:
            with _rate_limit_lock:
                _rate_limit_events.pop(request_bucket, None)


if __name__ == "__main__":
    unittest.main()
