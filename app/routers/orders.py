from typing import Any, List, Dict,Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus, DeliveryType, MangoType
from app.models.product import Product
from app.schemas.order import Order as OrderSchema, OrderCreate, OrderUpdate, MangoOrderItem
from app.services.delivery import delivery_service

router = APIRouter(prefix="/orders")

@router.get("/", response_model=List[OrderSchema])
def read_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
) -> Any:   
    """Retrieve user's orders with optional filtering"""
    # Start with base query
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    # Apply filters if provided
    if status:
        try:
            order_status = OrderStatus(status)
            query = query.filter(Order.status == order_status)
        except ValueError:
            # If invalid status is provided, ignore the filter
            pass
    
    # Filter by date range if provided
    if from_date:
        try:
            from_datetime = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            query = query.filter(Order.created_at >= from_datetime)
        except ValueError:
            # If invalid date format, ignore the filter
            pass
            
    if to_date:
        try:
            to_datetime = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
            query = query.filter(Order.created_at <= to_datetime)
        except ValueError:
            # If invalid date format, ignore the filter
            pass
    
    # Apply ordering, pagination and execute query
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderSchema)
def read_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get a specific order by id"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if the order belongs to the current user
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return order

@router.post("/", response_model=OrderSchema)
def create_order(
    *,
    db: Session = Depends(get_db),
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create new order"""
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    total_amount = 0.0
    order_items = []
    
    for item in order_in.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found")
        
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for product {product.name}")
        
        item_total = product.price * item.quantity
        total_amount += item_total
        
        # Create order item
        order_items.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": product.price,
            "total_price": item_total,
            "variation_name": product.variation_name,
        })
        
        # Update product stock
        product.stock -= item.quantity
        db.add(product)
    
    # Validate delivery options for mango orders
    if order_in.is_mango_delivery:
        if not order_in.mango_items or len(order_in.mango_items) == 0:
            raise HTTPException(status_code=400, detail="Mango items are required for mango delivery")
            
        # Check for zero quantities
        zero_quantity_items = [item for item in order_in.mango_items if item.quantity <= 0]
        if zero_quantity_items:
            raise HTTPException(status_code=400, detail="Quantity must be greater than zero for all mango items")
            
        # Extract mango types and quantities
        mango_types = [item.mango_type for item in order_in.mango_items]
        quantities = [item.quantity for item in order_in.mango_items]
        
        # Validate mango order based on delivery type
        is_valid, error_message, calculated_price = delivery_service.validate_mango_order(
            order_in.delivery_type.value, mango_types, quantities
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
            
        # Additional validation based on delivery type
        # if order_in.delivery_type == DeliveryType.PICKUP:
        #     # Validate airport code
        #     airports = delivery_service.get_airports()
        #     valid_airport = False
        #     for airport in airports:
        #         if airport['code'] == order_in.airport_code:
        #             valid_airport = True
        #             break
        #     if not valid_airport:
        #         raise HTTPException(status_code=400, detail=f"Invalid airport code: {order_in.airport_code}")
        
        elif order_in.delivery_type == DeliveryType.DOORSTEP:
            # Validate state and zipcode
            is_valid, error_message = delivery_service.validate_zipcode(order_in.shipping_zip, order_in.shipping_state)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_message)
                
            # Validate total quantity for doorstep delivery (must be 2 or 4)
            total_quantity = sum(quantities)
            allowed_quantities = delivery_service.get_doorstep_allowed_quantities()
            if total_quantity not in allowed_quantities:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Doorstep delivery only allows {allowed_quantities} boxes in total"
                )
                
            # Validate that no more than 2 mango types are mixed
            unique_mango_types = set(mango_types)
            if len(unique_mango_types) > 2:
                raise HTTPException(
                    status_code=400, 
                    detail="Doorstep delivery allows a maximum of 2 different mango types"
                )
                
            # Update price based on state for doorstep delivery
            calculated_price = delivery_service.calculate_doorstep_price(order_in.shipping_state, total_quantity)
            
        # Override the total amount with the calculated price for mango orders
        total_amount = calculated_price
    
    # Create order
    order = Order(
        order_number=order_number,
        total_amount=total_amount,
        status=OrderStatus.PROCESSING,
        delivery_type=order_in.delivery_type,
        is_mango_delivery=order_in.is_mango_delivery,
        shipping_zip=order_in.shipping_zip,
        shipping_address=order_in.shipping_address,
        shipping_state=order_in.shipping_state,
        airport_code=order_in.airport_code,
        airport_name=order_in.airport_name,
        payment_id=order_in.payment_id,
        user_id=current_user.id,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Create order items
    if order_in.is_mango_delivery and order_in.mango_items:
        # For mango orders, create order items based on mango_items
        for mango_item in order_in.mango_items:
            # Find the product ID for this mango type
            product = db.query(Product).filter(Product.type == mango_item.mango_type).first()
            if not product:
                # If product doesn't exist, create a placeholder for this mango type
                product = Product(
                    name=f"{mango_item.mango_type} Mango",
                    description=f"Premium Pakistani {mango_item.mango_type} Mango",
                    price=0.0,  # Price is calculated based on quantity and type
                    type=mango_item.mango_type,
                    stock=100  # Placeholder stock
                )
                db.add(product)
                db.commit()
                db.refresh(product)
            
            # For simplicity, we'll calculate a per-box price
            # This is a simplification as different mango types might have different prices
            total_boxes = sum(item.quantity for item in order_in.mango_items)
            unit_price = calculated_price / total_boxes if total_boxes > 0 else 0
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=mango_item.quantity,
                unit_price=unit_price,
                total_price=unit_price * mango_item.quantity,
                mango_type=mango_item.mango_type,
                variation_name=product.variation_name
            )
            db.add(order_item)
    else:
        # For regular orders, use the standard approach
        for item_data in order_items:
            order_item = OrderItem(
                order_id=order.id,
                **item_data
            )
            db.add(order_item)
    
    db.commit()
    db.refresh(order)
    
    return order

@router.put("/{order_id}", response_model=OrderSchema)
def update_order_status(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    order_in: OrderUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update order status (admin only)"""
    # Only admins can update order status
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update order status
    if order_in.status is not None:
        order.status = order_in.status
    
    # Update payment status
    if order_in.payment_status is not None:
        order.payment_status = order_in.payment_status
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order

@router.delete("/{order_id}", response_model=OrderSchema)
def cancel_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Cancel an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if the order belongs to the current user
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if the order can be cancelled
    if order.status != OrderStatus.PROCESSING:
        raise HTTPException(status_code=400, detail=f"Cannot cancel order with status {order.status}")
    
    # Update order status to cancelled
    order.status = OrderStatus.CANCELLED
    
    # Return items to stock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock += item.quantity
            db.add(product)
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order
