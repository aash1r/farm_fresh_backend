from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Shared properties
class ProductBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    type: str = "Mango"
    variation_name: Optional[str] = None  # e.g., "Pack of 2", "Pack of 4", "Box of 8"
    stock: int = 0

# Properties to receive via API on creation
class ProductCreate(ProductBase):
    pass

# Properties to receive via API on update
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    type: Optional[str] = None
    variation_name: Optional[str] = None
    stock: Optional[int] = None

# Properties shared by models stored in DB
class ProductInDBBase(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Properties to return to client
class Product(ProductInDBBase):
    pass
