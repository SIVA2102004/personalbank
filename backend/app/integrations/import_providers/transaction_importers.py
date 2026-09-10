from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class NormalizedTransaction(BaseModel):
    amount: float
    type: str  # DEBIT, CREDIT
    account_identifier: str
    merchant: Optional[str] = None
    reference: Optional[str] = None
    external_id: Optional[str] = None
    date: datetime
    source: str
    purpose: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None

class BaseTransactionImportProvider(ABC):
    @abstractmethod
    def fetch_or_parse_transactions(self, data: Any) -> List[NormalizedTransaction]:
        pass

class BankStatementImportProvider(BaseTransactionImportProvider):
    """Parses standard CSV/Excel or JSON statement records."""
    def fetch_or_parse_transactions(self, data: List[Dict[str, Any]]) -> List[NormalizedTransaction]:
        normalized = []
        for row in data:
            amt = float(row.get("amount", 0.0))
            tx_type = "CREDIT" if str(row.get("type", "")).upper() in ["CR", "CREDIT", "DEPOSIT"] else "DEBIT"
            normalized.append(NormalizedTransaction(
                amount=abs(amt),
                type=tx_type,
                account_identifier=str(row.get("account", "Main")),
                merchant=row.get("description", row.get("narration")),
                reference=str(row.get("ref_no", "")),
                date=datetime.utcnow(),
                source="STATEMENT_IMPORT",
                purpose=row.get("description")
            ))
        return normalized

class NotificationTransactionProvider(BaseTransactionImportProvider):
    """Normalizes user-permitted device transactional alerts."""
    def fetch_or_parse_transactions(self, data: Dict[str, Any]) -> List[NormalizedTransaction]:
        text = str(data.get("body", ""))
        # Example parsing: "Debited INR 450.00 from A/C XX1234 to Swiggy on 10-09-26"
        return [
            NormalizedTransaction(
                amount=float(data.get("amount", 100.0)),
                type="DEBIT" if "debited" in text.lower() or "spent" in text.lower() else "CREDIT",
                account_identifier=str(data.get("account", "Default")),
                merchant=str(data.get("merchant", "Merchant")),
                reference=str(data.get("ref", "")),
                date=datetime.utcnow(),
                source="NOTIFICATION",
                purpose=str(data.get("purpose", text[:50]))
            )
        ]
