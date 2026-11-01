import os, secrets, string
from decimal import Decimal
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

engine=create_engine(os.getenv("DATABASE_URL", "postgresql+psycopg://marasses:marasses@localhost:5432/marasses"), pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine, expire_on_commit=False)
app=FastAPI(title="Marasses API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["GET","POST"], allow_headers=["*"])
def db():
    session=SessionLocal()
    try: yield session
    finally: session.close()

@app.get("/api/categories")
def categories(s: Session=Depends(db)):
    return [dict(r) for r in s.execute(text("SELECT id,name,slug,description FROM categories WHERE is_active ORDER BY name")).mappings()]
@app.get("/api/products")
def products(s: Session=Depends(db)):
    rows=s.execute(text("""SELECT p.id product_id,p.name,p.slug,p.description,p.is_discreet,c.name category, v.id variant_id,v.sku,v.variant_name,v.price,v.stock_quantity FROM products p LEFT JOIN categories c ON c.id=p.category_id JOIN product_variants v ON v.product_id=p.id WHERE p.is_active ORDER BY p.name,v.price""")).mappings()
    result={}
    for r in rows:
        p=result.setdefault(str(r['product_id']), {"id":str(r['product_id']),"name":r['name'],"slug":r['slug'],"description":r['description'],"is_discreet":r['is_discreet'],"category":r['category'],"variants":[]})
        p['variants'].append({"id":str(r['variant_id']),"sku":r['sku'],"name":r['variant_name'],"price":float(r['price']),"stock":r['stock_quantity']})
    return list(result.values())
@app.get("/api/delivery-zones")
def zones(s: Session=Depends(db)):
    return [dict(r) for r in s.execute(text("SELECT id,name,neighborhoods,fee,estimated_delay FROM delivery_zones WHERE is_active ORDER BY name")).mappings()]
class Item(BaseModel): variant_id:str; quantity:int=Field(gt=0,le=50)
class OrderIn(BaseModel):
    delivery_zone_id:str; customer_alias:str|None=Field(default=None,max_length=100)
    customer_phone:str=Field(min_length=6,max_length=20); delivery_address:str=Field(min_length=3,max_length=500)
    payment_method:str=Field(min_length=2,max_length=50); items:list[Item]=Field(min_length=1,max_length=30)
@app.post("/api/orders", status_code=201)
def create_order(data:OrderIn,s:Session=Depends(db)):
    try:
        zone=s.execute(text("SELECT id,fee FROM delivery_zones WHERE id=:id AND is_active FOR SHARE"),{"id":data.delivery_zone_id}).mappings().first()
        if not zone: raise HTTPException(400,"Zone de livraison invalide")
        subtotal=Decimal('0'); lines=[]
        # Lock variants and validate all quantities before writing any order rows.
        for item in data.items:
            v=s.execute(text("SELECT id,price,stock_quantity FROM product_variants WHERE id=:id FOR UPDATE"),{"id":item.variant_id}).mappings().first()
            if not v or v['stock_quantity']<item.quantity: raise HTTPException(409,"Stock insuffisant pour un article")
            subtotal += v['price']*item.quantity; lines.append((v,item.quantity))
        fee=zone['fee']; number='CMD-'+''.join(secrets.choice(string.digits) for _ in range(8))
        s.execute(text("INSERT INTO orders(order_number,delivery_zone_id,customer_alias,customer_phone,delivery_address,subtotal_amount,delivery_fee,total_amount,payment_method) VALUES(:n,:z,:a,:p,:d,:s,:f,:t,:m)"),{"n":number,"z":data.delivery_zone_id,"a":data.customer_alias,"p":data.customer_phone,"d":data.delivery_address,"s":subtotal,"f":fee,"t":subtotal+fee,"m":data.payment_method})
        oid=s.execute(text("SELECT id FROM orders WHERE order_number=:n"),{"n":number}).scalar_one()
        for v,q in lines:
            s.execute(text("INSERT INTO order_items(order_id,product_variant_id,unit_price,quantity) VALUES(:o,:v,:p,:q)"),{"o":oid,"v":v['id'],"p":v['price'],"q":q})
            s.execute(text("UPDATE product_variants SET stock_quantity=stock_quantity-:q WHERE id=:v"),{"q":q,"v":v['id']})
        s.commit()
        return {"order_number":number,"subtotal":float(subtotal),"delivery_fee":float(fee),"total":float(subtotal+fee),"status":"processing"}
    except HTTPException:
        s.rollback(); raise
    except Exception:
        s.rollback(); raise
