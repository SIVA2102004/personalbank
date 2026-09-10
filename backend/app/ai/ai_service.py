import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import Transaction, Account, TransactionType

class CategorizationService:
    CATEGORY_KEYWORDS = {
        "Food": ["swiggy", "zomato", "restaurant", "cafe", "mcdonalds", "burger", "pizza", "lunch", "dinner", "breakfast", "groceries", "supermarket", "blinkit", "zepto", "instamart"],
        "Transportation": ["uber", "ola", "rapido", "metro", "fuel", "petrol", "diesel", "parking", "toll", "bus", "flight", "irctc", "train"],
        "Education": ["college", "fees", "books", "tuition", "course", "udemy", "coursera", "school", "exam"],
        "Shopping": ["amazon", "flipkart", "myntra", "clothes", "electronics", "mall", "shoes", "zara"],
        "Bills": ["electricity", "water", "wifi", "internet", "airtel", "jio", "recharge", "broadband", "rent", "gas"],
        "Entertainment": ["netflix", "spotify", "prime", "movie", "cinema", "theatre", "steam", "gaming"],
        "Healthcare": ["pharmacy", "apollo", "medplus", "doctor", "hospital", "clinic", "lab", "medicine"],
        "Salary": ["salary", "payroll", "stipend", "wages"],
        "Personal": ["ravi", "priya", "amit", "gift", "donation", "friend"]
    }

    @classmethod
    def predict_category(cls, merchant: Optional[str], description: Optional[str], amount: Optional[float]) -> Dict[str, Any]:
        text = f"{merchant or ''} {description or ''}".lower()
        
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    sub = "Food Delivery" if kw in ["swiggy", "zomato"] else ("Cab Service" if kw in ["uber", "ola"] else None)
                    return {
                        "category": category,
                        "sub_category": sub,
                        "confidence": 0.94
                    }
        
        return {
            "category": "Other",
            "sub_category": "General",
            "confidence": 0.50
        }

class PurposeExtractionService:
    @classmethod
    def extract_purpose(cls, raw_text: str, merchant: Optional[str] = None) -> str:
        text = raw_text.strip()
        if not text and merchant:
            return f"Payment to {merchant}"
        return text or "General payment"

class VoiceParsingService:
    @classmethod
    def parse_speech_to_transaction(cls, speech: str) -> Dict[str, Any]:
        text = speech.lower()
        
        amount = 0.0
        amt_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:rupees|rs|inr|₹)?', text)
        if amt_match:
            try:
                amount = float(amt_match.group(1))
            except Exception:
                pass
                
        person = None
        for name in ["ravi", "priya", "siva", "amit", "rahul", "neha", "arun"]:
            if name in text:
                person = name.capitalize()
                break

        purpose = "Payment"
        category = "Other"
        for kw in ["lunch", "dinner", "food", "college books", "uber", "groceries", "rent", "tea", "coffee"]:
            if kw in text:
                purpose = kw.capitalize()
                cat_info = CategorizationService.predict_category(None, kw, amount)
                category = cat_info["category"]
                break

        account_hint = "SBI" if "sbi" in text else ("HDFC" if "hdfc" in text else ("Cash" if "cash" in text else "Default"))
        method = "UPI" if "upi" in text else ("CASH" if "cash" in text else "BANK_TRANSFER")

        return {
            "understood": True,
            "raw_text": speech,
            "extracted": {
                "amount": amount,
                "person": person,
                "purpose": purpose,
                "category": category,
                "account_hint": account_hint,
                "payment_method": method
            }
        }

class ReceiptExtractionService:
    @classmethod
    def process_receipt_image(cls, image_url: Optional[str] = None) -> Dict[str, Any]:
        return {
            "merchant": "Reliance Smart Superstore",
            "date": datetime.utcnow().strftime("%d %b %Y"),
            "total": 1245.50,
            "tax": 62.50,
            "items": [
                {"name": "Organic Milk 1L", "price": 68.0, "qty": 2},
                {"name": "Whole Wheat Bread", "price": 45.0, "qty": 1},
                {"name": "Basmati Rice 5kg", "price": 620.0, "qty": 1},
                {"name": "Fresh Apples 1kg", "price": 180.0, "qty": 1},
                {"name": "Olive Oil 500ml", "price": 332.50, "qty": 1}
            ],
            "category": "Food",
            "payment_method": "UPI"
        }

class FinancialAssistantService:
    """
    STRICT GUARDRAILS:
    - Never invent transaction data
    - Answer ONLY based on authorized financial records
    - Clearly state if data is missing
    """
    @classmethod
    def answer_query(cls, db: Session, user_id: str, query: str) -> Dict[str, Any]:
        q = query.lower()

        # Check balance in an account (e.g., "in SBI", "SBI balance")
        if "sbi" in q:
            account = db.query(Account).filter(Account.user_id == user_id, Account.account_name.ilike("%sbi%")).first()
            if account:
                return {
                    "answer": f"Your tracked SBI balance is ₹{account.current_balance:,.2f}.",
                    "type": "BALANCE",
                    "data": {"account": account.account_name, "balance": account.current_balance}
                }
            return {"answer": "I could not find an SBI account in your financial records."}

        if "hdfc" in q:
            account = db.query(Account).filter(Account.user_id == user_id, Account.account_name.ilike("%hdfc%")).first()
            if account:
                return {
                    "answer": f"Your tracked HDFC balance is ₹{account.current_balance:,.2f}.",
                    "type": "BALANCE",
                    "data": {"account": account.account_name, "balance": account.current_balance}
                }
            return {"answer": "I could not find an HDFC account in your financial records."}

        # Check food expenses
        if "food" in q and ("spend" in q or "spent" in q or "expense" in q):
            total_food = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
                Transaction.user_id == user_id,
                Transaction.category == "Food",
                Transaction.transaction_type == TransactionType.DEBIT,
                Transaction.status == "SUCCESS"
            ).scalar()
            
            count_food = db.query(func.count(Transaction.id)).filter(
                Transaction.user_id == user_id,
                Transaction.category == "Food",
                Transaction.transaction_type == TransactionType.DEBIT,
                Transaction.status == "SUCCESS"
            ).scalar()

            return {
                "answer": f"You spent ₹{total_food:,.2f} on food across {count_food} transactions.",
                "type": "CATEGORY_SUMMARY",
                "data": {"category": "Food", "amount": total_food, "count": count_food}
            }

        # Largest expense
        if "largest" in q or "biggest" in q:
            largest = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.DEBIT,
                Transaction.status == "SUCCESS"
            ).order_by(Transaction.amount.desc()).first()

            if largest:
                date_str = largest.transaction_date.strftime("%B %d")
                return {
                    "answer": f"Your largest expense was ₹{largest.amount:,.2f} for '{largest.purpose}' on {date_str}.",
                    "type": "LARGEST_EXPENSE",
                    "data": {"amount": largest.amount, "purpose": largest.purpose, "date": str(largest.transaction_date)}
                }
            return {"answer": "You don't have any debit transactions recorded yet."}

        # Total balance
        if "total balance" in q or "total money" in q or "how much money do i have" in q:
            total = db.query(func.coalesce(func.sum(Account.current_balance), 0.0)).filter(
                Account.user_id == user_id,
                Account.is_active == True
            ).scalar()
            return {
                "answer": f"Your total tracked balance across all active accounts is ₹{total:,.2f}.",
                "type": "TOTAL_BALANCE",
                "data": {"total_balance": total}
            }

        # Person check
        for person in ["ravi", "priya", "amit", "rahul"]:
            if person in q:
                paid_sum = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
                    Transaction.user_id == user_id,
                    Transaction.person_name.ilike(f"%{person}%"),
                    Transaction.transaction_type == TransactionType.DEBIT,
                    Transaction.status == "SUCCESS"
                ).scalar()
                return {
                    "answer": f"You have paid ₹{paid_sum:,.2f} to {person.capitalize()} based on your recorded transactions.",
                    "type": "PERSON_EXPENSE",
                    "data": {"person": person.capitalize(), "amount": paid_sum}
                }

        return {
            "answer": "I don't have enough transaction data to determine that. Please check your accounts and transaction ledger for exact records.",
            "type": "UNKNOWN"
        }
