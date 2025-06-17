from typing import Any
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.payment import (
    PaymentResponse,
    ClientToken,
    PaymentTokenRequest,
)
from app.services.payment import payment_service

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/payments")


@router.get("/checkout")
async def payment_checkout(
    amount: float,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    
    token = auth_header.split(" ")[1]
    url = f"https://mypaymenthtml.s3.us-east-1.amazonaws.com/payment_checkout.html?amount={amount}&auth_token={token}"
    return {"checkout_url": url}

@router.post("/process-token", response_model=PaymentResponse)
async def process_payment_token(
    *,
    payment_in: PaymentTokenRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Process tokenized payment from Accept.js"""
    try:
        success, message, transaction_id = payment_service.process_payment_token(
            amount=payment_in.amount,
            data_descriptor=payment_in.data_descriptor,
            data_value=payment_in.data_value,
            first_name=payment_in.first_name,
            last_name=payment_in.last_name,
            order_description=payment_in.order_description,
            invoice_number=payment_in.invoice_number,
        )
        return PaymentResponse(success=success, message=message, transaction_id=transaction_id)
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



# @router.post("/process", response_model=PaymentResponse)
# async def process_payment(
#     *,
#     payment_in: PaymentRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ) -> Any:
#     """Process a payment through Authorize.Net"""
#     try:
#         success, message, transaction_id = payment_service.process_payment(
#             amount=payment_in.amount,
#             card_number=payment_in.card_number,
#             expiration_date=payment_in.expiration_date,
#             card_code=payment_in.card_code,
#             first_name=payment_in.first_name,
#             last_name=payment_in.last_name,
#             order_description=payment_in.order_description,
#             invoice_number=payment_in.invoice_number,
#         )
        
#         return PaymentResponse(
#             success=success,
#             message=message,
#             transaction_id=transaction_id
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Payment processing error: {str(e)}")


