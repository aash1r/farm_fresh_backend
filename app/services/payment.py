import logging
import uuid
from typing import Dict, Any, Optional, Tuple

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController, ARBCreateSubscriptionController
from authorizenet.constants import constants

from app.core.payment_config import authorize_net_settings

# Set up logging
logger = logging.getLogger("payment_service")

# Attach handlers from Gunicorn if running under Gunicorn
gunicorn_logger = logging.getLogger("gunicorn.error")
if gunicorn_logger.handlers:
    logger.handlers = gunicorn_logger.handlers
    logger.setLevel(gunicorn_logger.level)
else:
    # Fallback to console handler
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
        print(self.api_login_id)
        print(self.transaction_key)
        print(self.client_key)
        print(self.sandbox_mode)

    def get_merchant_auth(self) -> apicontractsv1.merchantAuthenticationType:
        """Get merchant authentication for Authorize.Net API"""
        merchant_auth = apicontractsv1.merchantAuthenticationType()
        merchant_auth.name = self.api_login_id
        merchant_auth.transactionKey = self.transaction_key
        return merchant_auth

    def get_client_token(self) -> Dict[str, str]:
        """Get client token for client-side payment processing
        
        Returns:
            Dictionary with client key and API login ID
        """
        return {
            "clientKey": self.client_key,
            "apiLoginID": self.api_login_id
        }


    def process_payment_token(
        self,
        amount: float,
        data_descriptor: str,
        data_value: str,
        first_name: str,
        last_name: str,
        # order_description: str = "Farm Fresh Shop Order",
        # invoice_number: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[str]]:
        """Process a payment using the opaque token from Accept.js

        Args:
            amount: Transaction amount
            data_descriptor: Opaque data descriptor from Accept.js
            data_value: Opaque data value from Accept.js
            first_name: Customer first name
            last_name: Customer last name
        """

        merchant_auth = self.get_merchant_auth()

        # Create opaque payment type
        opaque = apicontractsv1.opaqueDataType()
        opaque.dataDescriptor = data_descriptor
        opaque.dataValue = data_value

        payment = apicontractsv1.paymentType()
        payment.opaqueData = opaque

        # Customer information
        customer = apicontractsv1.customerDataType()
        logger.info(f"customer: {customer}")
        # customer.id = uuid.uuid4().hex[:20]
        customer.email = f"{first_name.lower()}.{last_name.lower()}@example.com"

        # Billing name (optional but good practice)
        # bill_to = apicontractsv1.customerAddressType()
        # bill_to.firstName = first_name
        # bill_to.lastName = last_name
        # print("bill_to:", bill_to)

        transaction_request = apicontractsv1.transactionRequestType()
        transaction_request.transactionType = "authCaptureTransaction"
        transaction_request.amount = amount
        transaction_request.payment = payment
        transaction_request.customer = customer
        # transaction_request.billTo = bill_to
        # if order_description:
        #     transaction_request.order = apicontractsv1.orderType()
        #     transaction_request.order.description = order_description
        # if invoice_number:
        #     if not transaction_request.order:
        #         transaction_request.order = apicontractsv1.orderType()
        #     transaction_request.order.invoiceNumber = invoice_number[:20]

        request = apicontractsv1.createTransactionRequest()
        request.merchantAuthentication = merchant_auth
        request.transactionRequest = transaction_request

        controller = createTransactionController(request)
        if self.sandbox_mode:
            controller.setenvironment(constants.SANDBOX)
        controller.execute()

        response = controller.getresponse()
        logger.info(f"Authorize.Net response: {response}")

        if response and response.messages.resultCode == "Ok":
            trans_id = getattr(response.transactionResponse, "transId", None)
            logger.info(f"Transaction successful. ID: {trans_id}")
            return True, "Payment processed successfully", str(trans_id)
        
        message = "Payment failed"
        if response:
            try:
                if hasattr(response, "transactionResponse") and hasattr(response.transactionResponse, "errors"):
                    error_text = response.transactionResponse.errors.error[0].errorText
                    error_code = response.transactionResponse.errors.error[0].errorCode
                    message = f"{error_code}: {error_text}"
                elif hasattr(response, "messages") and hasattr(response.messages, "message"):
                    message = response.messages.message[0].text
            except Exception as e:
                logger.exception("Error parsing payment failure response")

        logger.error(f"Transaction failed: {message}")
        return False, message, None

payment_service = PaymentService()
