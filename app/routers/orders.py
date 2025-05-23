from typing import Any, List, Dict, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.payment import PaymentRequest, PaymentResponse
from app.services.payment import payment_service
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus, DeliveryType, MangoType
from app.models.product import Product
from app.schemas.order import Order as OrderSchema, OrderCreate, OrderUpdate, MangoOrderItem, PayAndCreateOrderRequest, PayAndCreateOrderResponse, OrderList
from app.services.delivery import delivery_service
from app.services.payment import payment_service

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

# Enhanced endpoint for order tracking without validation errors
@router.get("/my-orders", response_model=List[OrderList])
def track_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    sort_by: Optional[str] = "created_at",  # Sort by field
    sort_desc: bool = True,  # Sort direction
    current_user: User = Depends(get_current_user),
) -> Any:
    """Track user's orders with enhanced sorting and filtering"""
    # Start with base query
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    # Apply status filter if provided
    if status:
        try:
            order_status = OrderStatus(status)
            query = query.filter(Order.status == order_status)
        except ValueError:
            # If invalid status is provided, ignore the filter
            pass
    
    # Apply sorting
    if sort_by == "total_amount":
        order_col = Order.total_amount
    elif sort_by == "status":
        order_col = Order.status
    else:  # Default to created_at
        order_col = Order.created_at
    
    # Apply sort direction
    if sort_desc:
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())
    
    # Apply pagination and execute query
    orders = query.offset(skip).limit(limit).all()
    return orders

# @router.get("/{order_id}", response_model=OrderSchema)
# def read_order(
#     order_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ) -> Any:
#     """Get a specific order by id"""
#     order = db.query(Order).filter(Order.id == order_id).first()
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")
    
#     # Check if the order belongs to the current user
#     if order.user_id != current_user.id and not current_user.is_admin:
#         raise HTTPException(status_code=403, detail="Not enough permissions")
    
#     return order

@router.post("/", response_model=PayAndCreateOrderResponse)
def create_order(
    *,
    db: Session = Depends(get_db),
    request: PayAndCreateOrderRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create new order"""

    try:
        success, message, transaction_id = payment_service.process_payment(
            amount=request.amount,
            card_number=request.card_number,
            expiration_date=request.expiration_date,
            card_code=request.card_code,
            first_name=request.first_name,
            last_name=request.last_name,
            order_description=request.order_description,
            invoice_number=request.invoice_number,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment processing error: {str(e)}")


    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    total_amount = 0.0
    order_items = []
    
    for item in request.items:
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
    if request.is_mango_delivery:
        if not request.mango_items or len(request.mango_items) == 0:
            raise HTTPException(status_code=400, detail="Mango items are required for mango delivery")
            
        # Check for zero quantities
        zero_quantity_items = [item for item in request.mango_items if item.quantity <= 0]
        if zero_quantity_items:
            raise HTTPException(status_code=400, detail="Quantity must be greater than zero for all mango items")
            
        # Extract mango types and quantities
        mango_types = [item.mango_type for item in request.mango_items]
        quantities = [item.quantity for item in request.mango_items]
        
        # Validate mango order based on delivery type
        is_valid, error_message, calculated_price = delivery_service.validate_mango_order(
            request.delivery_type.value, mango_types, quantities
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
        
        elif request.delivery_type == DeliveryType.DOORSTEP:
            # Validate state and zipcode
            is_valid, error_message = delivery_service.validate_zipcode(request.shipping_zip, request.shipping_state)
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
            calculated_price = delivery_service.calculate_doorstep_price(request.shipping_state, total_quantity)
            
        # Override the total amount with the calculated price for mango orders
        total_amount = calculated_price
    
    # Create order
    order = Order(
        order_number=order_number,
        total_amount=total_amount,
        status=OrderStatus.PROCESSING,
        delivery_type=request.delivery_type,
        is_mango_delivery=request.is_mango_delivery,
        shipping_zip=request.shipping_zip,
        shipping_address=request.shipping_address,
        shipping_state=request.shipping_state,
        airport_code=request.airport_code,
        airport_name=request.airport_name,
        payment_id=transaction_id,  # Use the transaction_id from payment processing
        user_id=current_user.id,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Create order items
    if request.is_mango_delivery and request.mango_items:
        # For mango orders, create order items based on mango_items
        for mango_item in request.mango_items:
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
            total_boxes = sum(item.quantity for item in request.mango_items)
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
    
    # Convert SQLAlchemy model to Pydantic model for serialization
    order_schema = OrderSchema.model_validate(order)
    
    return PayAndCreateOrderResponse(
            success=success,
            message=message,
            order=order_schema,
            transaction_id=transaction_id
        )    

# Enhanced endpoint for order tracking
@router.get("/my-orders", response_model=List[OrderSchema])
def track_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    sort_by: Optional[str] = "created_at",  # New: sort by field
    sort_desc: bool = True,  # New: sort direction
    current_user: User = Depends(get_current_user),
) -> Any:
    """Track user's orders with enhanced sorting and filtering"""
    # Start with base query
    query = db.query(Order).filter(Order.user_id == current_user.id)
    
    # Apply status filter if provided
    if status:
        try:
            order_status = OrderStatus(status)
            query = query.filter(Order.status == order_status)
        except ValueError:
            # If invalid status is provided, ignore the filter
            pass
    
    # Apply sorting
    if sort_by == "total_amount":
        order_col = Order.total_amount
    elif sort_by == "status":
        order_col = Order.status
    else:  # Default to created_at
        order_col = Order.created_at
    
    # Apply sort direction
    if sort_desc:
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())
    
    # Apply pagination and execute query
    orders = query.offset(skip).limit(limit).all()
    return orders

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

