from typing import Optional, List, Dict
from pydantic import BaseModel, validator, Field
from datetime import datetime
from app.models.order import OrderStatus, DeliveryType, MangoType

# Order Item Schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: Optional[float] = None
    total_price: float
    mango_type: Optional[str] = None  # For mango orders

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemInDBBase(OrderItemBase):
    id: int
    order_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class OrderItem(OrderItemInDBBase):
    product_name: Optional[str] = None
    variation_name: Optional[str] = None

# Order Schemas
class MangoOrderItem(BaseModel):
    mango_type: str
    quantity: int
    
    @validator('mango_type')
    def validate_mango_type(cls, v):
        valid_types = [mango.value for mango in MangoType]
        if v not in valid_types:
            raise ValueError(
                f"Invalid mango type: {v}. "
                f"Must be one of: Sindhri, Langhra, Chaunsa, or Ratol"
            )
        return v

class OrderBase(BaseModel):
    delivery_type: DeliveryType
    shipping_zip: str
    payment_id: str
    is_mango_delivery: bool = False
    
    # Optional fields based on delivery type
    shipping_address: Optional[str] = None
    shipping_state: Optional[str] = None
    airport_code: Optional[str] = None
    airport_name: Optional[str] = None
    
    # Mango-specific fields
    # mango_items: Optional[List[MangoOrderItem]] = None
    
    @validator('shipping_state')
    def validate_doorstep_fields(cls, v, values):
        if values.get('delivery_type') == DeliveryType.DOORSTEP and v is None:
            field_name = 'shipping_state' if v is None else 'shipping_address'
            raise ValueError(f'{field_name} is required for doorstep delivery')
        return v
    
    @validator('airport_name')
    def validate_pickup_fields(cls, v, values):
        if values.get('delivery_type') == DeliveryType.PICKUP and v is None:
            field_name = 'airport_name' if v is None else 'airport_code'
            raise ValueError(f'{field_name} is required for pickup delivery')
        return v

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    # Payment information is now handled separately through the payment service

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[str] = None

class OrderInDBBase(OrderBase):
    id: int
    order_number: str
    total_amount: float
    status: OrderStatus
    # payment_status: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Order(OrderInDBBase):
    items: List[OrderItem] = []
