from typing import Any, List, Dict, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator

from app.core.deps import get_db
from app.models.user import User
from app.models.order import DeliveryType, MangoType
from app.services.delivery import delivery_service

# Define request and response models for mango orders
class MangoOrderItem(BaseModel):
    mango_type: str
    quantity: int
    
    @validator('mango_type')
    def validate_mango_type(cls, v):
        valid_types = [mango.value for mango in MangoType]
        if v not in valid_types:
            raise ValueError(f"Invalid mango type: {v}. Must be one of {valid_types}")
        return v

class MangoOrderRequest(BaseModel):
    delivery_type: str
    items: List[MangoOrderItem]
    state: Optional[str] = None  # Required for doorstep delivery
    
    @validator('delivery_type')
    def validate_delivery_type(cls, v):
        valid_types = [delivery.value for delivery in DeliveryType]
        if v not in valid_types:
            raise ValueError(f"Invalid delivery type: {v}. Must be one of {valid_types}")
        return v
    
    @validator('state')
    def validate_state(cls, v, values):
        if values.get('delivery_type') == DeliveryType.DOORSTEP.value and not v:
            raise ValueError("State is required for doorstep delivery")
        return v

class MangoOrderResponse(BaseModel):
    valid: bool
    message: Optional[str] = None
    total_price: float = 0.0

router = APIRouter(prefix="/delivery")

@router.get("/airports", response_model=List[Dict[str, str]])
def get_airports() -> Any:
    """Get list of available airports for mango pickup"""
    try:
        airports = delivery_service.get_airports()
        return airports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading airport data: {str(e)}")

@router.get("/states", response_model=List[str])
def get_states() -> Any:
    """Get list of available states for doorstep delivery"""
    try:
        states = delivery_service.get_available_states()
        return states
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading state data: {str(e)}")

@router.get("/validate-zipcode")
def validate_zipcode(
    zipcode: str = Query(..., description="Zipcode to validate"),
    state: str = Query(..., description="State code (e.g., IL, NY)"),
) -> Dict[str, Any]:
    """Validate if zipcode is available for delivery in the given state"""
    try:
        is_valid, error_message = delivery_service.validate_zipcode(zipcode, state)
        return {
            "valid": is_valid,
            "message": error_message if not is_valid else "Zipcode is valid for delivery"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating zipcode: {str(e)}")

@router.get("/mango-types", response_model=List[str])
def get_mango_types() -> Any:
    """Get list of available mango types"""
    try:
        mango_types = delivery_service.get_mango_types()
        return mango_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading mango types: {str(e)}")

@router.get("/allowed-quantities/{delivery_type}", response_model=List[int])
def get_allowed_quantities(delivery_type: str) -> Any:
    """Get allowed quantities based on delivery type"""
    try:
        if delivery_type == DeliveryType.PICKUP.value:
            return delivery_service.get_pickup_allowed_quantities()
        elif delivery_type == DeliveryType.DOORSTEP.value:
            return delivery_service.get_doorstep_allowed_quantities()
        else:
            raise HTTPException(status_code=400, detail=f"Invalid delivery type: {delivery_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting allowed quantities: {str(e)}")

@router.post("/validate-mango-order", response_model=MangoOrderResponse)
def validate_mango_order(order: MangoOrderRequest = Body(...)) -> Any:
    """Validate mango order based on delivery type and selection rules"""
    try:
        # Extract mango types and quantities from the request
        mango_types = [item.mango_type for item in order.items]
        quantities = [item.quantity for item in order.items]
        
        # Validate the order
        is_valid, error_message, total_price = delivery_service.validate_mango_order(
            order.delivery_type, mango_types, quantities
        )
        
        # If doorstep delivery, update price based on state
        if is_valid and order.delivery_type == DeliveryType.DOORSTEP.value:
            total_quantity = sum(quantities)
            total_price = delivery_service.calculate_doorstep_price(order.state, total_quantity)
        
        return {
            "valid": is_valid,
            "message": error_message if not is_valid else "Order is valid",
            "total_price": total_price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating mango order: {str(e)}")

@router.get("/calculate-price")
def calculate_price(
    delivery_type: str = Query(..., description="Delivery type (pickup or doorstep)"),
    mango_type: str = Query(None, description="Mango type (required for pickup)"),
    quantity: int = Query(..., description="Total quantity of boxes"),
    state: str = Query(None, description="State code (required for doorstep)"),
) -> Dict[str, Any]:
    """Calculate price based on delivery type, mango type, quantity, and state"""
    try:
        if delivery_type == DeliveryType.PICKUP.value:
            if not mango_type:
                raise HTTPException(status_code=400, detail="Mango type is required for pickup delivery")
            price = delivery_service.calculate_pickup_price(mango_type, quantity)
        elif delivery_type == DeliveryType.DOORSTEP.value:
            if not state:
                raise HTTPException(status_code=400, detail="State is required for doorstep delivery")
            price = delivery_service.calculate_doorstep_price(state, quantity)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid delivery type: {delivery_type}")
        
        return {
            "price": price
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating price: {str(e)}")
