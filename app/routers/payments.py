from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.payment import PaymentRequest, PaymentResponse, ClientToken
from app.services.payment import payment_service

router = APIRouter(prefix="/payments")


@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    *,
    payment_in: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Process a payment through Authorize.Net"""
    try:
        success, message, transaction_id = payment_service.process_payment(
            amount=payment_in.amount,
            card_number=payment_in.card_number,
            expiration_date=payment_in.expiration_date,
            card_code=payment_in.card_code,
            first_name=payment_in.first_name,
            last_name=payment_in.last_name,
            order_description=payment_in.order_description,
            invoice_number=payment_in.invoice_number,
        )
        
        return PaymentResponse(
            success=success,
            message=message,
            transaction_id=transaction_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment processing error: {str(e)}")


@router.get("/client-token", response_model=ClientToken)
async def get_client_token(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get client token for client-side payment processing"""
    try:
        token = payment_service.get_client_token()
        return token
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting client token: {str(e)}")
