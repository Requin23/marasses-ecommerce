import unittest
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from fastapi import HTTPException
from starlette.requests import Request

from app.main import (
    Item,
    OrderIn,
    SupportRequestIn,
    _rate_limit_events,
    _rate_limit_lock,
    rate_limit,
)


def make_request(ip_address: str) -> Request:
    return Request({
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/test",
        "raw_path": b"/test",
        "query_string": b"",
        "headers": [],
        "client": (ip_address, 12345),
        "server": ("testserver", 80),
    })


class OrderValidationTests(unittest.TestCase):
    def base_order(self, **overrides):
        values = {
            "delivery_zone_id": str(uuid4()),
            "customer_phone": "+22670000000",
            "delivery_address": "Ouagadougou, secteur 15",
            "items": [{"variant_id": str(uuid4()), "quantity": 1}],
        }
        values.update(overrides)
        return values

    def test_order_without_location_is_allowed(self):
        order = OrderIn(**self.base_order())
        self.assertIsNone(order.delivery_latitude)
        self.assertFalse(order.delivery_location_consent)

    def test_coordinates_require_explicit_consent(self):
        with self.assertRaises(ValueError):
            OrderIn(**self.base_order(delivery_latitude=12.37, delivery_longitude=-1.52))

    def test_coordinates_must_be_provided_as_a_pair(self):
        with self.assertRaises(ValueError):
            OrderIn(**self.base_order(delivery_latitude=12.37, delivery_location_consent=True))

    def test_consent_requires_coordinates(self):
        with self.assertRaises(ValueError):
            OrderIn(**self.base_order(delivery_location_consent=True))

    def test_quantity_must_be_between_one_and_fifty(self):
        for quantity in (0, 51):
            with self.subTest(quantity=quantity), self.assertRaises(ValueError):
                Item(variant_id=uuid4(), quantity=quantity)

    def test_support_request_requires_consent_and_valid_message(self):
        values = {"customer_phone": "+22670000000", "topic": "Commande", "message": "Ma commande est en retard", "consent": True}
        self.assertEqual(SupportRequestIn(**values).topic, "Commande")
        with self.assertRaises(ValueError):
            SupportRequestIn(**{**values, "consent": False})


class ConcurrentRateLimitTests(unittest.TestCase):
    def test_only_limit_number_of_simultaneous_requests_pass(self):
        bucket = "unit-test-concurrency"
        with _rate_limit_lock:
            _rate_limit_events.pop((bucket, "198.51.100.42"), None)
        check = rate_limit(bucket, 5, 60)

        def attempt(_):
            try:
                check(make_request("198.51.100.42"))
                return True
            except HTTPException as exc:
                if exc.status_code != 429:
                    raise
                return False

        try:
            with ThreadPoolExecutor(max_workers=20) as pool:
                results = list(pool.map(attempt, range(20)))
            self.assertEqual(sum(results), 5)
        finally:
            with _rate_limit_lock:
                _rate_limit_events.pop((bucket, "198.51.100.42"), None)


if __name__ == "__main__":
    unittest.main()
