from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import re


class PaymentRequest(BaseModel):
    """Schema for payment request"""
    amount: float = Field(..., gt=0, description="Payment amount")
    card_number: str = Field(..., min_length=13, max_length=16, description="Credit card number")
    expiration_date: str = Field(..., description="Card expiration date in MMYY format")
    card_code: str = Field(..., min_length=3, max_length=4, description="CVV/security code")
    first_name: str = Field(..., description="Customer's first name")
    last_name: str = Field(..., description="Customer's last name")
    order_description: Optional[str] = Field("Farm Fresh Shop Order", description="Description of the order")
    invoice_number: Optional[str] = Field(None, description="Invoice number")
    
    @validator('card_number')
    def validate_card_number(cls, v):
        # Remove any spaces or dashes
        v = re.sub(r'[\s-]', '', v)
        # Check if it's all digits
        if not v.isdigit():
            raise ValueError("Card number must contain only digits")
        # Check length (most cards are 13-16 digits)
        if len(v) < 13 or len(v) > 16:
            raise ValueError("Card number must be between 13 and 16 digits")
        return v
    
    @validator('expiration_date')
    def validate_expiration_date(cls, v):
        # Remove any spaces or slashes
        v = re.sub(r'[\s/]', '', v)
        # Check if it's in MMYY format
        if not re.match(r'^(0[1-9]|1[0-2])\d{2}$', v):
            raise ValueError("Expiration date must be in MMYY format (e.g., 0125 for January 2025)")
        return v
    
    @validator('card_code')
    def validate_card_code(cls, v):
        # Check if it's all digits
        if not v.isdigit():
            raise ValueError("Card code must contain only digits")
        # Check length (3-4 digits)
        if len(v) < 3 or len(v) > 4:
            raise ValueError("Card code must be 3 or 4 digits")
        return v


class PaymentResponse(BaseModel):
    """Schema for payment response"""
    success: bool = Field(..., description="Whether the payment was successful")
    message: str = Field(..., description="Message describing the result")
    transaction_id: Optional[str] = Field(None, description="Transaction ID if successful")


class ClientToken(BaseModel):
    """Schema for client token response"""
    clientKey: str = Field(..., description="Client key for Authorize.Net Accept.js")
    apiLoginID: str = Field(..., description="API Login ID for Authorize.Net Accept.js")
