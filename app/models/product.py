from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    type = Column(String, index=True, nullable=False, default="Mango")  # Type of mango (e.g., Sindhri, Chaunsa)
    variation_name = Column(String, nullable=True)  # Variation name (e.g., "Pack of 2", "Pack of 4", "Box of 8")
    stock = Column(Integer, default=0, nullable=True)  # Track available quantity
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="product")
