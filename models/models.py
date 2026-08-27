from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import create_engine
from pydantic import BaseModel, AnyUrl, validator
from sqlalchemy.orm import Session

DATABASE_URL = "sqlite:///database/price_tracker.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, future=True)

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    shop = Column(String(100), nullable=True)
    check_interval_minutes = Column(Integer, default=60)  # 取得間隔（分）
    last_price = Column(Integer, nullable=True)  # 現在価格（整数：円単位が想定）
    previous_price = Column(Integer, nullable=True)
    last_checked_at = Column(DateTime, nullable=True)
    disabled = Column(Boolean, default=False)

    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    price = Column(Integer, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(255), nullable=True)
    currency = Column(String(10), default="JPY")
    http_status = Column(Integer, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    product = relationship("Product", back_populates="price_history")

# --- Pydantic schemas for API (basic) ---
class ProductCreateSchema(BaseModel):
    name: str
    url: AnyUrl
    shop: Optional[str] = None
    check_interval_minutes: Optional[int] = 60

    @validator("check_interval_minutes")
    def interval_allowed(cls, v):
        allowed = [15,30,60,180,360,720,1440]
        if v not in allowed:
            raise ValueError(f"check_interval_minutes must be one of {allowed}")
        return v

class ProductSchema(ProductCreateSchema):
    id: int
    last_price: Optional[int] = None
    previous_price: Optional[int] = None
    last_checked_at: Optional[datetime] = None
    disabled: bool = False

    class Config:
        orm_mode = True

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
