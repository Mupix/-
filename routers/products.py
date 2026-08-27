from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from models.models import Product, ProductCreateSchema, ProductSchema, get_db
from pydantic import AnyUrl
from urllib.parse import urlparse
import socket
import ipaddress

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


def is_private_hostname(hostname: str) -> bool:
    # Prevent SSRF by rejecting hostnames that resolve to private/loopback addresses
    try:
        infos = socket.getaddrinfo(hostname, None)
        for info in infos:
            addr = info[4][0]
            try:
                ip = ipaddress.ip_address(addr)
                if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                    return True
            except Exception:
                # if it's not an IP, skip
                continue
    except Exception:
        # If DNS resolution fails, treat as not private (let other checks handle it)
        return False
    return False


@router.get("", response_model=List[ProductSchema])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products


@router.post("", response_model=ProductSchema, status_code=201)
def create_product(payload: ProductCreateSchema, db: Session = Depends(get_db)):
    url = str(payload.url)
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.hostname:
        raise HTTPException(status_code=400, detail="不正なURLです。")
    # Basic scheme whitelist
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="URL スキームは http または https のみ許可されています。")
    # SSRF prevention: hostname must not resolve to private ip
    if is_private_hostname(parsed.hostname):
        raise HTTPException(status_code=400, detail="指定された URL のホストは内部ネットワークに属しているため許可されません。")
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


@router.put("/{product_id}", response_model=ProductSchema)
def update_product(product_id: int, payload: ProductCreateSchema, db: Session = Depends(get_db)):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    url = str(payload.url)
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.hostname:
        raise HTTPException(status_code=400, detail="不正なURLです。")
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="URL スキームは http または https のみ許可されています。")
    if is_private_hostname(parsed.hostname):
        raise HTTPException(status_code=400, detail="指定された URL のホストは内部ネットワークに属しているため許可されません。")
    p.name = payload.name
    p.url = url
    p.shop = payload.shop or detect_shop_from_url(url)
    p.check_interval_minutes = payload.check_interval_minutes
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(p)
    db.commit()
    return


@router.post("/{product_id}/refresh")
def refresh_product(product_id: int, db: Session = Depends(get_db)):
    # Phase2: Stub for manual refresh. Phase5/9 will implement actual fetching and scheduling.
    p = db.get(Product, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    # For now, just respond that a refresh was triggered. In future, enqueue a job.
    return {"status": "ok", "message": "価格取得を開始しました（スタブ）。"}
