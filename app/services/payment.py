import logging
import uuid
from typing import Dict, Any, Optional, Tuple

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController, ARBCreateSubscriptionController
from authorizenet.constants import constants

from app.core.payment_config import authorize_net_settings

# Set up logging
logger = logging.getLogger("payment_service")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class PaymentService:
    """Service for handling payments through Authorize.Net"""

    def __init__(self):
        self.api_login_id = authorize_net_settings.api_login_id
        self.transaction_key = authorize_net_settings.transaction_key
        self.client_key = authorize_net_settings.client_key
        self.sandbox_mode = authorize_net_settings.sandbox_mode

    def get_merchant_auth(self) -> apicontractsv1.merchantAuthenticationType:
        """Get merchant authentication for Authorize.Net API"""
        merchant_auth = apicontractsv1.merchantAuthenticationType()
        merchant_auth.name = self.api_login_id
        merchant_auth.transactionKey = self.transaction_key
        return merchant_auth

    def process_payment(
        self,
        amount: float,
        card_number: str,
        expiration_date: str,  # Format: "MMYY"
        card_code: str,
        first_name: str,
        last_name: str,
        order_description: str = "Farm Fresh Shop Order",
        invoice_number: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[str]]:
        """Process a payment through Authorize.Net
        
        Args:
            amount: The payment amount
            card_number: Credit card number
            expiration_date: Expiration date in MMYY format
            card_code: CVV/security code
            first_name: Customer's first name
            last_name: Customer's last name
            order_description: Description of the order
            invoice_number: Optional invoice number
            
        Returns:
            Tuple containing:
            - success: Boolean indicating if payment was successful
            - message: Message describing the result
            - transaction_id: Transaction ID if successful, None otherwise
        """
        # Create a transaction
        transaction = apicontractsv1.transactionRequestType()
        transaction.transactionType = "authCaptureTransaction"
        transaction.amount = str(amount)
        
        # Set payment information
        payment = apicontractsv1.paymentType()
        credit_card = apicontractsv1.creditCardType()
        credit_card.cardNumber = card_number
        credit_card.expirationDate = expiration_date
        credit_card.cardCode = card_code
        payment.creditCard = credit_card
        transaction.payment = payment
        
        # Set order information
        if not invoice_number:
            invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        
        order = apicontractsv1.orderType()
        order.invoiceNumber = invoice_number
        order.description = order_description
        transaction.order = order
        
        # Set customer information
        customer_data = apicontractsv1.customerDataType()
        customer_data.type = "individual"
        customer_data.id = str(uuid.uuid4())
        customer_data.email = ""  # Could be added as a parameter if needed
        transaction.customer = customer_data
        
        # Set billing information
        billing_address = apicontractsv1.customerAddressType()
        billing_address.firstName = first_name
        billing_address.lastName = last_name
        transaction.billTo = billing_address
        
        # Create request and controller
        create_transaction = apicontractsv1.createTransactionRequest()
        create_transaction.merchantAuthentication = self.get_merchant_auth()
        create_transaction.refId = str(uuid.uuid4())
        create_transaction.transactionRequest = transaction
        
        # Execute request
        controller = createTransactionController(create_transaction)
        if self.sandbox_mode:
            controller.setenvironment(constants.SANDBOX)
        else:
            controller.setenvironment(constants.PRODUCTION)
            
        controller.execute()
        
        # Get response
        response = controller.getresponse()
        
        if response is not None:
            if response.messages.resultCode == "Ok":
                if hasattr(response.transactionResponse, 'transId'):
                    transaction_id = response.transactionResponse.transId
                    return True, "Payment processed successfully", transaction_id
                else:
                    return False, "Payment processed but no transaction ID was returned", None
            else:
                error_message = f"Payment failed: {response.messages.message[0].text}"
                if hasattr(response, 'transactionResponse') and hasattr(response.transactionResponse, 'errors'):
                    error_message += f" - {response.transactionResponse.errors.error[0].errorText}"
                return False, error_message, None
        else:
            return False, "No response from payment gateway", None

    def get_client_token(self) -> Dict[str, str]:
        """Get client token for client-side payment processing
        
        Returns:
            Dictionary with client key and API login ID
        """
        return {
            "clientKey": self.client_key,
            "apiLoginID": self.api_login_id
        }


# Create a singleton instance
payment_service = PaymentService()
