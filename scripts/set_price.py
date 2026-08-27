#!/usr/bin/env python
# scripts/set_price.py
# 使い方 (Windows cmd):
#   .venv\Scripts\activate.bat
#   python scripts\set_price.py <product_id> <price>

import sys
from datetime import datetime
import os

# Ensure project root is importable
sys.path.append(os.path.abspath("."))

from models.models import SessionLocal, Product, PriceHistory


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/set_price.py <product_id> <price>")
        return 1

    try:
        product_id = int(sys.argv[1])
        price = int(float(sys.argv[2]))
    except Exception as e:
        print("Invalid arguments:", e)
        return 2

    db = SessionLocal()
    p = db.get(Product, product_id)
    if not p:
        print(f"Product not found: {product_id}")
        return 3

    # update previous_price and last_price
    p.previous_price = p.last_price
    p.last_price = price
    p.last_checked_at = datetime.utcnow()

    ph = PriceHistory(
        product_id=p.id,
        price=price,
        checked_at=p.last_checked_at,
        source="manual",
        currency="JPY",
        http_status=None,
        success=True,
        error_message=None
    )

    db.add(ph)
    db.add(p)
    db.commit()
    print(f"Updated product {p.id} ({p.name}) -> last_price={p.last_price}")
    db.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
