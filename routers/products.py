from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from models.models import Product, ProductCreateSchema, ProductSchema, get_db
from pydantic import AnyUrl
from urllib.parse import urlparse

router = APIRouter()

def detect_shop_from_url(url: str) -> str:
    try:
        hostname = urlparse(url).hostname or ""
        hostname = hostname.replace("www.", "")
        if "amazon.co.jp" in hostname or "amazon." in hostname:
            return "Amazon"
        if "rakuten.co.jp" in hostname:
            return "楽天市場"
        if "shopping.yahoo.co.jp" in hostname or "yahoo.co.jp" in hostname:
            return "Yahoo!ショッピング"
        return "その他"
    except Exception:
        return "その他"

@router.get("", response_model=List[ProductSchema])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

@router.post("", response_model=ProductSchema, status_code=201)
def create_product(payload: ProductCreateSchema, db: Session = Depends(get_db)):
    # 簡易 URL セーフチェック（Pydantic AnyUrl により基本的なバリデーションは済）
    url = str(payload.url)
    # SSRF予防: 単純なチェック — ホスト名が存在することを確認
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.hostname:
        raise HTTPException(status_code=400, detail="不正なURLです。")
    shop = payload.shop or detect_shop_from_url(url)
    product = Product(
        name=payload.name,
        url=url,
        shop=shop,
        check_interval_minutes=payload.check_interval_minutes
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/{product_id}", response_model=ProductSchema)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p

@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(p)
    db.commit()
    return
