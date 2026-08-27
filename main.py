from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from models.models import Base, engine, get_db
from routers import products as products_router
from services import scheduler as scheduler_service

app = FastAPI(title="PriceTracker - Phase1")

# テンプレートと静的ファイル
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ルータ登録
app.include_router(products_router.router, prefix="/api/products", tags=["products"])

@app.on_event("startup")
def on_startup():
    # ディレクトリと DB の作成
    os.makedirs("database", exist_ok=True)
    # テーブル作成
    Base.metadata.create_all(bind=engine)
    # スケジューラの初期化（Phase1 はスタブ）
    scheduler_service.start_scheduler()
    print("Startup complete: DB initialized and scheduler started (stub).")

@app.get("/", include_in_schema=False)
def index(request: Request):
    # トップページ（テンプレート）へ
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/product/{product_id}", include_in_schema=False)
def product_page(request: Request, product_id: int, db: Session = Depends(get_db)):
    # 商品ページ（テンプレート）へ
    return templates.TemplateResponse("product.html", {"request": request, "product_id": product_id})
