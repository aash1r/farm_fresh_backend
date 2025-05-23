from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base

class OrderStatus(str, enum.Enum):
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class DeliveryType(str, enum.Enum):
    PICKUP = "pickup"
    DOORSTEP = "doorstep"

class MangoType(str, enum.Enum):
    SINDHRI = "Sindhri"
    LANGHRA = "Langhra"
    CHAUNSA = "Chaunsa"
    RATOL = "Ratol"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PROCESSING)
    
    # Delivery information
    delivery_type = Column(Enum(DeliveryType), nullable=False)
    is_mango_delivery = Column(Boolean, default=False)  # Flag to identify mango deliveries
    
    # For both delivery types
    shipping_zip = Column(String, nullable=True)
    
    # For doorstep delivery
    shipping_address = Column(String, nullable=True)
    shipping_state = Column(String, nullable=True)
    
    # For airport pickup
    airport_code = Column(String, nullable=True)
    airport_name = Column(String, nullable=True)
    
    payment_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    mango_type = Column(String, nullable=True)  # For mango orders
    variation_name = Column(String, nullable=True)  # For product variations (e.g., "Pack of 2", "Box of 8")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign keys
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
