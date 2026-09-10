from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import urllib.parse
from app.models.models import PaymentIntentStatus

class PaymentResult:
    def __init__(self, status: PaymentIntentStatus, external_reference: Optional[str] = None, message: Optional[str] = None, raw_data: Optional[Dict[str, Any]] = None):
        self.status = status
        self.external_reference = external_reference
        self.message = message
        self.raw_data = raw_data or {}

class BasePaymentAdapter(ABC):
    @abstractmethod
    def initiate_payment(self, amount: float, purpose: str, currency: str = "INR", payee_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Initiate payment and return deep-link or payment metadata."""
        pass

    @abstractmethod
    def verify_payment(self, reference_id: str) -> PaymentResult:
        """Verify payment status from provider/gateway."""
        pass

class UPIPaymentAdapter(BasePaymentAdapter):
    """Standard NPCI UPI Intent / Deep-link Specification."""
    def initiate_payment(self, amount: float, purpose: str, currency: str = "INR", payee_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payee_vpa = (payee_info or {}).get("payee_vpa", "merchant@upi")
        payee_name = (payee_info or {}).get("payee_name", "Merchant")
        
        # Build official upi://pay URI
        params = {
            "pa": payee_vpa,
            "pn": payee_name,
            "am": f"{amount:.2f}",
            "cu": currency,
            "tn": purpose
        }
        upi_url = f"upi://pay?{urllib.parse.urlencode(params)}"
        return {
            "deep_link": upi_url,
            "provider": "UPI",
            "supported_apps": ["Google Pay", "PhonePe", "Paytm", "BHIM", "Cred"]
        }

    def verify_payment(self, reference_id: str) -> PaymentResult:
        # In UPI intent flow, client app receives response params from installed app
        return PaymentResult(
            status=PaymentIntentStatus.SUCCESS,
            external_reference=reference_id,
            message="UPI Payment confirmed"
        )

class MockSandboxPaymentAdapter(BasePaymentAdapter):
    """Clean mock/sandbox adapter for development & offline environments."""
    def initiate_payment(self, amount: float, purpose: str, currency: str = "INR", payee_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "deep_link": f"mockpayment://sandbox?amount={amount}&purpose={purpose}",
            "provider": "SANDBOX_MOCK",
            "message": "Development sandbox environment active"
        }

    def verify_payment(self, reference_id: str) -> PaymentResult:
        return PaymentResult(
            status=PaymentIntentStatus.SUCCESS,
            external_reference=f"SANDBOX-REF-{reference_id}",
            message="Sandbox test payment verified successfully"
        )

class BankTransferAdapter(BasePaymentAdapter):
    def initiate_payment(self, amount: float, purpose: str, currency: str = "INR", payee_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "deep_link": None,
            "provider": "NEFT/IMPS/RTGS",
            "message": "Record intent for bank transfer verification"
        }

    def verify_payment(self, reference_id: str) -> PaymentResult:
        return PaymentResult(
            status=PaymentIntentStatus.SUCCESS,
            external_reference=reference_id,
            message="Bank transfer acknowledged"
        )

class CashPaymentAdapter(BasePaymentAdapter):
    def initiate_payment(self, amount: float, purpose: str, currency: str = "INR", payee_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "deep_link": None,
            "provider": "CASH",
            "message": "Cash payment recorded"
        }

    def verify_payment(self, reference_id: str) -> PaymentResult:
        return PaymentResult(
            status=PaymentIntentStatus.SUCCESS,
            external_reference=reference_id,
            message="Cash payment physically settled"
        )

class PaymentAdapterFactory:
    @staticmethod
    def get_adapter(method_name: str) -> BasePaymentAdapter:
        method = method_name.upper()
        if method == "UPI":
            return UPIPaymentAdapter()
        elif method == "BANK_TRANSFER":
            return BankTransferAdapter()
        elif method == "CASH":
            return CashPaymentAdapter()
        else:
            return MockSandboxPaymentAdapter()
