"""Read-only smoke/load profile. Run only against local or staging deployments."""

from locust import HttpUser, between, task


class StorefrontVisitor(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def browse_products(self):
        self.client.get("/api/products", name="GET /api/products")

    @task(3)
    def browse_delivery_zones(self):
        self.client.get("/api/delivery-zones", name="GET /api/delivery-zones")

    @task(1)
    def check_api_health(self):
        self.client.get("/api/health", name="GET /api/health")
