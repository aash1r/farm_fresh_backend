from typing import Tuple
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderUpdate
from app.services.delivery import delivery_service
from app.models.order import DeliveryType
from app.models.order import OrderStatus
from app.models.product import Product
from typing import List
from app.schemas.order import PayAndCreateOrderRequest

def handle_regular_order_logic(db: Session, request: PayAndCreateOrderRequest) -> Tuple[float, List[dict]]:
    total = 0.0
    items = []

    for item in request.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")

        item_total = product.price * item.quantity
        total += item_total
        product.stock -= item.quantity
        db.add(product)

        items.append({
            "product_id": product.id,
            "quantity": item.quantity,
            "unit_price": product.price,
            "total_price": item_total,
            "variation_name": product.variation_name,
            "type": product.type,
        })
    return total, items

def handle_mango_order_logic(db: Session, request: PayAndCreateOrderRequest) -> Tuple[float, List[dict]]:
    mango_items = request.mango_items or []
    if not mango_items:
        raise HTTPException(status_code=400, detail="Mango items required")

    for item in mango_items:
        if item.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    mango_types = [item.mango_type for item in mango_items]
    quantities = [item.quantity for item in mango_items]

    is_valid, error, price = delivery_service.validate_mango_order(
        request.delivery_type.value, mango_types, quantities
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    if request.delivery_type == DeliveryType.DOORSTEP:
        is_valid, error = delivery_service.validate_zipcode(request.shipping_zip, request.shipping_state)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)

        total_quantity = sum(quantities)
        allowed = delivery_service.get_doorstep_allowed_quantities()
        if total_quantity not in allowed:
            raise HTTPException(status_code=400, detail=f"Doorstep delivery allows only {allowed} boxes")

        if len(set(mango_types)) > 2:
            raise HTTPException(status_code=400, detail="Max 2 mango types allowed for doorstep")

        price = delivery_service.calculate_doorstep_price(request.shipping_state, total_quantity)

    items_data = []
    total_boxes = sum(item.quantity for item in mango_items)
    unit_price = price / total_boxes if total_boxes else 0

    for mango_item in mango_items:
        product = db.query(Product).filter(Product.type == mango_item.mango_type).first()
        if not product:
            product = Product(
                name=f"{mango_item.mango_type} Mango",
                description=f"Premium {mango_item.mango_type} Mango",
                price=0.0,
                type=mango_item.mango_type,
                stock=100,
            )
            db.add(product)
            db.flush()

        items_data.append({
            "product_id": product.id,
            "quantity": mango_item.quantity,
            "unit_price": unit_price,
            "total_price": unit_price * mango_item.quantity,
            "mango_type": mango_item.mango_type,
            "variation_name": product.variation_name,
        })

    return price, items_data
