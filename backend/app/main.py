import hashlib
import hmac
import json
import os
import base64
import secrets
import string
import time
from decimal import Decimal
from typing import Literal
from urllib.parse import urlencode, urlparse
from uuid import UUID

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://marasses:marasses@localhost:5432/marasses")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL.removeprefix("postgres://")
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL.removeprefix("postgresql://")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
app = FastAPI(title="Marasses API", version="0.2.0")
cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)

GENIUSPAY_API = "https://geniuspay.ci/api/v1/merchant"


def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _admin_token(expiry: int, key: str) -> str:
    payload = base64.urlsafe_b64encode(str(expiry).encode()).decode().rstrip("=")
    signature = hmac.new(key.encode(), payload.encode(), hashlib.sha256).digest()
    return payload + "." + base64.urlsafe_b64encode(signature).decode().rstrip("=")


def require_admin(request: Request):
    key = os.getenv("ADMIN_API_KEY", "").strip()
    if len(key) < 32:
        raise HTTPException(503, "L’accès administrateur n’est pas configuré.")
    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    try:
        payload, signature = token.split(".", 1)
        expected = hmac.new(key.encode(), payload.encode(), hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))
        expiry = int(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)).decode())
    except (ValueError, TypeError):
        raise HTTPException(401, "Session administrateur invalide ou expirée.")
    if scheme.lower() != "bearer" or not hmac.compare_digest(expected, supplied) or expiry < int(time.time()):
        raise HTTPException(401, "Session administrateur invalide ou expirée.")
    return True


class AdminLoginIn(BaseModel):
    password: str = Field(min_length=1, max_length=256)


@app.post("/api/admin/login")
def admin_login(data: AdminLoginIn):
    key = os.getenv("ADMIN_API_KEY", "").strip()
    if len(key) < 32:
        raise HTTPException(503, "L’accès administrateur n’est pas configuré.")
    if not hmac.compare_digest(data.password.encode(), key.encode()):
        raise HTTPException(401, "Mot de passe incorrect.")
    return {"token": _admin_token(int(time.time()) + 12 * 60 * 60, key), "expires_in": 43200}


@app.get("/api/admin/orders", dependencies=[Depends(require_admin)])
def admin_orders(s: Session = Depends(db)):
    rows = s.execute(text("""SELECT o.id,o.order_number,o.customer_alias,o.customer_phone,o.delivery_address,
        o.delivery_latitude,o.delivery_longitude,o.delivery_location_accuracy_m,o.delivery_location_consent_at,
        o.subtotal_amount,o.delivery_fee,o.total_amount,o.payment_method,o.payment_status,o.order_status,
        o.payment_reference,o.created_at,z.name AS zone
        FROM orders o LEFT JOIN delivery_zones z ON z.id=o.delivery_zone_id
        ORDER BY o.created_at DESC LIMIT 100""")).mappings().all()
    if not rows:
        return []
    ids = [row["id"] for row in rows]
    items = s.execute(text("""SELECT oi.order_id,p.name AS product_name,pv.variant_name,oi.unit_price,oi.quantity
        FROM order_items oi JOIN product_variants pv ON pv.id=oi.product_variant_id
        JOIN products p ON p.id=pv.product_id WHERE oi.order_id=ANY(:ids)
        ORDER BY p.name"""), {"ids": ids}).mappings().all()
    by_order = {order_id: [] for order_id in ids}
    for item in items:
        by_order[item["order_id"]].append({"product": item["product_name"], "variant": item["variant_name"], "unit_price": float(item["unit_price"]), "quantity": item["quantity"]})
    result = []
    for row in rows:
        order = dict(row)
        order["id"] = str(order["id"])
        order["items"] = by_order[row["id"]]
        for field in ("subtotal_amount", "delivery_fee", "total_amount"):
            order[field] = float(order[field])
        result.append(order)
    return result


@app.get("/api/admin/products", dependencies=[Depends(require_admin)])
def admin_products(s: Session = Depends(db)):
    rows = s.execute(text("""SELECT p.id AS product_id,p.name,p.is_active,c.name AS category,
        v.id AS variant_id,v.variant_name,v.price,v.stock_quantity
        FROM products p LEFT JOIN categories c ON c.id=p.category_id
        JOIN product_variants v ON v.product_id=p.id ORDER BY p.name,v.price""")).mappings().all()
    return [{**dict(row), "product_id": str(row["product_id"]), "variant_id": str(row["variant_id"]), "price": float(row["price"])} for row in rows]


class AdminVariantUpdate(BaseModel):
    price: Decimal = Field(ge=0, le=100000000)
    stock_quantity: int = Field(ge=0, le=1000000)


@app.patch("/api/admin/variants/{variant_id}", dependencies=[Depends(require_admin)])
def admin_update_variant(variant_id: UUID, data: AdminVariantUpdate, s: Session = Depends(db)):
    result = s.execute(text("UPDATE product_variants SET price=:price,stock_quantity=:stock WHERE id=:id"), {"price": data.price, "stock": data.stock_quantity, "id": variant_id})
    if result.rowcount != 1:
        s.rollback()
        raise HTTPException(404, "Format de produit introuvable.")
    s.commit()
    return {"ok": True}


class AdminOrderUpdate(BaseModel):
    order_status: Literal["processing", "preparing", "shipped", "delivered"]


@app.patch("/api/admin/orders/{order_id}/status", dependencies=[Depends(require_admin)])
def admin_update_order(order_id: UUID, data: AdminOrderUpdate, s: Session = Depends(db)):
    result = s.execute(text("UPDATE orders SET order_status=:status WHERE id=:id AND payment_status NOT IN ('failed','cancelled','expired')"), {"status": data.order_status, "id": order_id})
    if result.rowcount != 1:
        s.rollback()
        raise HTTPException(404, "Commande introuvable ou paiement annulé.")
    s.commit()
    return {"ok": True}


@app.get("/api/health")
def health(s: Session = Depends(db)):
    try:
        s.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected", "geniuspay_configured": bool(os.getenv("GENIUSPAY_API_KEY") and os.getenv("GENIUSPAY_API_SECRET")), "geniuspay_environment": os.getenv("GENIUSPAY_ENVIRONMENT", "sandbox")}
    except Exception:
        raise HTTPException(503, "Base de données indisponible")


class SupportRequestIn(BaseModel):
    order_number: str | None = Field(default=None, max_length=20)
    customer_phone: str = Field(min_length=6, max_length=20)
    topic: Literal["Commande", "Livraison", "Paiement", "Produit", "Autre"]
    message: str = Field(min_length=10, max_length=2000)
    consent: bool = False
    website: str = Field(default="", max_length=200)

    @model_validator(mode="after")
    def validate_support_request(self):
        if not self.consent:
            raise ValueError("Votre accord est nécessaire pour traiter la réclamation.")
        if self.website.strip():
            raise ValueError("Demande invalide.")
        if self.order_number is not None:
            self.order_number = self.order_number.strip() or None
        self.customer_phone = self.customer_phone.strip()
        self.message = self.message.strip()
        return self


@app.post("/api/support-requests", status_code=201)
def create_support_request(data: SupportRequestIn, s: Session = Depends(db)):
    reference = "REC-" + "".join(secrets.choice(string.digits) for _ in range(8))
    try:
        s.execute(text("""INSERT INTO support_requests(
            reference,order_number,customer_phone,topic,message,consent_at
        ) VALUES(:reference,:order_number,:phone,:topic,:message,NOW())"""), {
            "reference": reference,
            "order_number": data.order_number,
            "phone": data.customer_phone,
            "topic": data.topic,
            "message": data.message,
        })
        s.commit()
        return {"reference": reference, "message": "Votre demande a bien été envoyée."}
    except Exception:
        s.rollback()
        raise HTTPException(503, "Impossible d’envoyer votre demande pour le moment. Réessayez plus tard.")


@app.get("/api/categories")
def categories(s: Session = Depends(db)):
    rows = s.execute(text("SELECT id,name,slug,description FROM categories WHERE is_active ORDER BY name"))
    return [dict(row) for row in rows.mappings()]


@app.get("/api/products")
def products(s: Session = Depends(db)):
    rows = s.execute(text("""SELECT p.id product_id,p.name,p.slug,p.description,p.is_discreet,c.name category,
        v.id variant_id,v.sku,v.variant_name,v.price,v.stock_quantity
        FROM products p LEFT JOIN categories c ON c.id=p.category_id
        JOIN product_variants v ON v.product_id=p.id
        WHERE p.is_active ORDER BY p.name,v.price""")).mappings()
    result = {}
    for row in rows:
        product = result.setdefault(str(row["product_id"]), {
            "id": str(row["product_id"]), "name": row["name"], "slug": row["slug"],
            "description": row["description"], "is_discreet": row["is_discreet"],
            "category": row["category"], "variants": [],
        })
        product["variants"].append({
            "id": str(row["variant_id"]), "sku": row["sku"], "name": row["variant_name"],
            "price": float(row["price"]), "stock": row["stock_quantity"],
        })
    return list(result.values())


@app.get("/api/delivery-zones")
def zones(s: Session = Depends(db)):
    rows = s.execute(text("SELECT id,name,neighborhoods,fee,estimated_delay FROM delivery_zones WHERE is_active ORDER BY name"))
    return [dict(row) for row in rows.mappings()]


class Item(BaseModel):
    variant_id: UUID
    quantity: int = Field(gt=0, le=50)


class OrderIn(BaseModel):
    delivery_zone_id: UUID
    customer_alias: str | None = Field(default=None, max_length=100)
    customer_phone: str = Field(min_length=6, max_length=20)
    delivery_address: str = Field(min_length=3, max_length=500)
    delivery_latitude: float | None = Field(default=None, ge=-90, le=90)
    delivery_longitude: float | None = Field(default=None, ge=-180, le=180)
    delivery_location_accuracy_m: float | None = Field(default=None, ge=0, le=100000)
    delivery_location_consent: bool = False
    payment_method: Literal["Paiement à la livraison", "GeniusPay"] = "Paiement à la livraison"
    items: list[Item] = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def validate_delivery_location(self):
        has_latitude = self.delivery_latitude is not None
        has_longitude = self.delivery_longitude is not None
        if has_latitude != has_longitude:
            raise ValueError("La latitude et la longitude doivent être fournies ensemble.")
        if has_latitude and not self.delivery_location_consent:
            raise ValueError("Le partage de la position nécessite un consentement explicite.")
        if self.delivery_location_accuracy_m is not None and not has_latitude:
            raise ValueError("La précision ne peut être enregistrée sans position.")
        if self.delivery_location_consent and not has_latitude:
            raise ValueError("Une position est nécessaire pour enregistrer ce consentement.")
        return self


async def create_geniuspay_checkout(order_number: str, amount: Decimal, phone: str, alias: str | None, status_token: str):
    api_key = os.getenv("GENIUSPAY_API_KEY", "").strip()
    api_secret = os.getenv("GENIUSPAY_API_SECRET", "").strip()
    if not api_key or not api_secret:
        raise HTTPException(503, "Le paiement en ligne n'est pas configuré.")

    public_url = os.getenv("APP_PUBLIC_URL", "http://localhost:3000").rstrip("/")
    success_url = f"{public_url}/paiement-retour?{urlencode({'commande': order_number, 'jeton': status_token, 'resultat': 'retour'})}"
    error_url = f"{public_url}/paiement-retour?{urlencode({'commande': order_number, 'jeton': status_token, 'resultat': 'annule'})}"
    payload = {
        "amount": int(amount),
        "currency": "XOF",
        "description": f"Commande Marasses {order_number}",
        "customer": {"name": alias or "Client Marasses", "phone": phone, "country": "BF"},
        "success_url": success_url,
        "error_url": error_url,
        "metadata": {"order_id": order_number},
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{GENIUSPAY_API}/payments",
                headers={"X-API-Key": api_key, "X-API-Secret": api_secret},
                json=payload,
            )
    except httpx.HTTPError:
        raise HTTPException(502, "GeniusPay est temporairement injoignable. La commande n'a pas été enregistrée.")

    if response.status_code >= 400:
        raise HTTPException(502, "GeniusPay n'a pas pu initialiser le paiement. Vérifiez les clés Sandbox.")
    try:
        payment = response.json().get("data", {})
        reference = payment.get("reference")
        checkout_url = payment.get("checkout_url") or payment.get("payment_url")
    except (ValueError, AttributeError):
        raise HTTPException(502, "Réponse de paiement GeniusPay invalide.")
    parsed_url = urlparse(checkout_url or "")
    if not reference or parsed_url.scheme != "https" or parsed_url.netloc not in {"geniuspay.ci", "pay.genius.ci"}:
        raise HTTPException(502, "GeniusPay a retourné une adresse de paiement invalide.")
    return reference, checkout_url


@app.post("/api/orders", status_code=201)
async def create_order(data: OrderIn, s: Session = Depends(db)):
    try:
        zone = s.execute(
            text("SELECT id,fee FROM delivery_zones WHERE id=:id AND is_active FOR SHARE"),
            {"id": data.delivery_zone_id},
        ).mappings().first()
        if not zone:
            raise HTTPException(400, "Zone de livraison invalide")

        subtotal = Decimal("0")
        lines = []
        for item in data.items:
            variant = s.execute(
                text("SELECT id,price,stock_quantity FROM product_variants WHERE id=:id FOR UPDATE"),
                {"id": item.variant_id},
            ).mappings().first()
            if not variant or variant["stock_quantity"] < item.quantity:
                raise HTTPException(409, "Stock insuffisant pour un article")
            subtotal += variant["price"] * item.quantity
            lines.append((variant, item.quantity))

        fee = zone["fee"]
        total = subtotal + fee
        order_number = "CMD-" + "".join(secrets.choice(string.digits) for _ in range(8))
        provider = reference = checkout_url = status_token = status_token_hash = None
        order_status = "processing"
        if data.payment_method == "GeniusPay":
            if total < Decimal("200"):
                raise HTTPException(400, "Le paiement GeniusPay doit être d'au moins 200 FCFA.")
            status_token = secrets.token_urlsafe(32)
            status_token_hash = hashlib.sha256(status_token.encode()).hexdigest()
            reference, checkout_url = await create_geniuspay_checkout(
                order_number, total, data.customer_phone, data.customer_alias, status_token
            )
            provider = "geniuspay"
            order_status = "awaiting_payment"

        s.execute(text("""INSERT INTO orders(
            order_number,delivery_zone_id,customer_alias,customer_phone,delivery_address,
            delivery_latitude,delivery_longitude,delivery_location_accuracy_m,delivery_location_consent_at,
            subtotal_amount,delivery_fee,total_amount,payment_method,payment_status,order_status,
            payment_provider,payment_reference,payment_checkout_url,payment_status_token_hash
        ) VALUES(:n,:z,:a,:p,:d,:latitude,:longitude,:accuracy,CASE WHEN :location_consent THEN NOW() ELSE NULL END,
            :subtotal,:fee,:total,:method,'pending',:status,:provider,:reference,:checkout,:token_hash)"""), {
            "n": order_number, "z": data.delivery_zone_id, "a": data.customer_alias,
            "p": data.customer_phone, "d": data.delivery_address, "subtotal": subtotal,
            "latitude": data.delivery_latitude, "longitude": data.delivery_longitude,
            "accuracy": data.delivery_location_accuracy_m, "location_consent": data.delivery_location_consent,
            "fee": fee, "total": total, "method": data.payment_method, "status": order_status,
            "provider": provider, "reference": reference, "checkout": checkout_url, "token_hash": status_token_hash,
        })
        order_id = s.execute(text("SELECT id FROM orders WHERE order_number=:n"), {"n": order_number}).scalar_one()
        for variant, quantity in lines:
            s.execute(text("INSERT INTO order_items(order_id,product_variant_id,unit_price,quantity) VALUES(:o,:v,:p,:q)"), {
                "o": order_id, "v": variant["id"], "p": variant["price"], "q": quantity,
            })
            s.execute(text("UPDATE product_variants SET stock_quantity=stock_quantity-:q WHERE id=:v"), {
                "q": quantity, "v": variant["id"],
            })
        s.commit()
        result = {
            "order_number": order_number, "subtotal": float(subtotal), "delivery_fee": float(fee),
            "total": float(total), "status": order_status,
        }
        if checkout_url:
            result["payment_url"] = checkout_url
            result["payment_reference"] = reference
        return result
    except HTTPException:
        s.rollback()
        raise
    except Exception:
        s.rollback()
        raise


@app.get("/api/orders/{order_number}/payment-status")
async def get_payment_status(order_number: str, token: str = Query(min_length=20, max_length=100), s: Session = Depends(db)):
    order = s.execute(text("SELECT id,total_amount,payment_status,payment_reference,payment_status_token_hash FROM orders WHERE order_number=:n AND payment_provider='geniuspay' FOR UPDATE"), {"n": order_number}).mappings().first()
    if not order or not order["payment_status_token_hash"]:
        raise HTTPException(404, "Commande introuvable.")
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    if not hmac.compare_digest(token_hash, order["payment_status_token_hash"]):
        raise HTTPException(404, "Commande introuvable.")
    if order["payment_status"] in {"completed", "failed", "cancelled", "expired"}:
        return {"order_number": order_number, "status": order["payment_status"]}

    api_key = os.getenv("GENIUSPAY_API_KEY", "").strip()
    api_secret = os.getenv("GENIUSPAY_API_SECRET", "").strip()
    if not api_key or not api_secret:
        raise HTTPException(503, "Vérification GeniusPay non configurée.")
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(f"{GENIUSPAY_API}/payments/{order['payment_reference']}", headers={"X-API-Key": api_key, "X-API-Secret": api_secret})
        response.raise_for_status()
        payment = response.json().get("data", {})
    except (httpx.HTTPError, ValueError):
        raise HTTPException(502, "GeniusPay est temporairement injoignable.")
    status = payment.get("status")
    if payment.get("reference") != order["payment_reference"]:
        raise HTTPException(502, "Référence GeniusPay incohérente.")
    if status == "completed":
        if Decimal(str(payment.get("amount", "0"))) != order["total_amount"] or payment.get("currency", "XOF") != "XOF":
            raise HTTPException(502, "Montant ou devise GeniusPay incohérent.")
        s.execute(text("UPDATE orders SET payment_status='completed',order_status='processing' WHERE id=:id AND payment_status IN ('pending','processing')"), {"id": order["id"]})
    elif status in {"failed", "cancelled", "expired"}:
        items = s.execute(text("SELECT product_variant_id,quantity FROM order_items WHERE order_id=:id"), {"id": order["id"]}).mappings()
        for item in items:
            s.execute(text("UPDATE product_variants SET stock_quantity=stock_quantity+:q WHERE id=:id"), {"q": item["quantity"], "id": item["product_variant_id"]})
        s.execute(text("UPDATE orders SET payment_status=:status,order_status='cancelled' WHERE id=:id AND payment_status IN ('pending','processing')"), {"status": status, "id": order["id"]})
    s.commit()
    return {"order_number": order_number, "status": status or order["payment_status"]}


@app.post("/api/webhooks/geniuspay")
async def geniuspay_webhook(request: Request, s: Session = Depends(db)):
    webhook_secret = os.getenv("GENIUSPAY_WEBHOOK_SECRET", "").strip()
    if not webhook_secret:
        raise HTTPException(503, "Webhook GeniusPay non configuré.")
    raw_body = await request.body()
    signature = request.headers.get("X-Webhook-Signature", "")
    timestamp = request.headers.get("X-Webhook-Timestamp", "")
    event_header = request.headers.get("X-Webhook-Event", "")
    environment = request.headers.get("X-Webhook-Environment", "")
    try:
        payload = json.loads(raw_body)
        timestamp_int = int(timestamp)
    except (ValueError, TypeError, json.JSONDecodeError):
        raise HTTPException(400, "Webhook invalide.")
    if abs(time.time() - timestamp_int) > 300:
        raise HTTPException(400, "Webhook expiré.")
    if environment != os.getenv("GENIUSPAY_ENVIRONMENT", "sandbox"):
        raise HTTPException(400, "Environnement de webhook incorrect.")

    signed_candidates = [f"{timestamp}.".encode() + raw_body]
    canonical = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode()
    signed_candidates.append(f"{timestamp}.".encode() + canonical)
    valid_signature = any(
        hmac.compare_digest(hmac.new(webhook_secret.encode(), signed, hashlib.sha256).hexdigest(), signature)
        for signed in signed_candidates
    )
    if not valid_signature:
        raise HTTPException(401, "Signature webhook invalide.")
    if event_header and payload.get("event") != event_header:
        raise HTTPException(400, "Événement webhook incohérent.")

    event = event_header or payload.get("event")
    data = payload.get("data") or {}
    metadata = data.get("metadata") or {}
    order_number = metadata.get("order_id")
    reference = data.get("reference")
    if event not in {"payment.success", "payment.failed", "payment.cancelled", "payment.expired"}:
        return {"received": True, "ignored": True}
    order = s.execute(text("SELECT id,total_amount,payment_status,order_status,payment_reference FROM orders WHERE order_number=:n FOR UPDATE"), {"n": order_number}).mappings().first()
    if not order or order["payment_reference"] != reference:
        s.rollback()
        raise HTTPException(404, "Commande ou référence de paiement inconnue.")
    if order["payment_status"] != "pending":
        s.commit()
        return {"received": True, "already_processed": True}
    if event == "payment.success":
        if Decimal(str(data.get("amount", "0"))) != order["total_amount"] or data.get("currency", "XOF") != "XOF":
            s.rollback()
            raise HTTPException(400, "Montant ou devise du paiement incorrect.")
        s.execute(text("UPDATE orders SET payment_status='completed',order_status='processing' WHERE id=:id"), {"id": order["id"]})
    else:
        items = s.execute(text("SELECT product_variant_id,quantity FROM order_items WHERE order_id=:id"), {"id": order["id"]}).mappings()
        for item in items:
            s.execute(text("UPDATE product_variants SET stock_quantity=stock_quantity+:q WHERE id=:id"), {
                "q": item["quantity"], "id": item["product_variant_id"],
            })
        s.execute(text("UPDATE orders SET payment_status=:status,order_status='cancelled' WHERE id=:id"), {
            "status": "failed" if event == "payment.failed" else event.removeprefix("payment."), "id": order["id"],
        })
    s.commit()
    return {"received": True}
