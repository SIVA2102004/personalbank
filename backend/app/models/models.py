import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Boolean, DateTime, ForeignKey, Enum, Text, Integer, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class AccountType(str, enum.Enum):
    BANK = "BANK"
    UPI = "UPI"
    CASH = "CASH"
    WALLET = "WALLET"
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    SAVINGS = "SAVINGS"
    INVESTMENT = "INVESTMENT"
    OTHER = "OTHER"

class TransactionType(str, enum.Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    TRANSFER = "TRANSFER"
    REFUND = "REFUND"
    ADJUSTMENT = "ADJUSTMENT"

class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"

class TransactionSource(str, enum.Enum):
    MANUAL = "MANUAL"
    PAYMENT_FLOW = "PAYMENT_FLOW"
    IMPORT = "IMPORT"
    VOICE = "VOICE"
    RECEIPT_SCAN = "RECEIPT_SCAN"
    BANK_SYNC = "BANK_SYNC"
    USER_CONFIRMED = "USER_CONFIRMED"

class PaymentMethod(str, enum.Enum):
    UPI = "UPI"
    BANK_TRANSFER = "BANK_TRANSFER"
    CARD = "CARD"
    CASH = "CASH"
    WALLET = "WALLET"
    OTHER = "OTHER"

class PaymentIntentStatus(str, enum.Enum):
    CREATED = "CREATED"
    INITIATED = "INITIATED"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"

class BudgetStatus(str, enum.Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    EXCEEDED = "EXCEEDED"

# --- Models ---

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    preferred_currency = Column(String(10), default="INR")
    country = Column(String(50), default="India")
    monthly_income = Column(Float, default=0.0)
    financial_goal = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    payment_intents = relationship("PaymentIntent", back_populates="user", cascade="all, delete-orphan")
    people = relationship("Person", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("SavingsGoal", back_populates="user", cascade="all, delete-orphan")
    recurring = relationship("RecurringTransaction", back_populates="user", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(Enum(AccountType), default=AccountType.BANK, nullable=False)
    institution_name = Column(String(100), nullable=False)
    masked_identifier = Column(String(50), nullable=True)
    opening_balance = Column(Float, default=0.0, nullable=False)
    current_balance = Column(Float, default=0.0, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    color = Column(String(20), default="#4361EE")
    icon = Column(String(50), default="account_balance")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")


class TransactionCategory(Base):
    __tablename__ = "transaction_categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False)
    subcategories = Column(JSON, default=list)  # list of strings
    icon = Column(String(50), default="category")
    color = Column(String(20), default="#3F37C9")
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    account_id = Column(String(36), ForeignKey("accounts.id"), index=True, nullable=False)
    transaction_type = Column(Enum(TransactionType), default=TransactionType.DEBIT, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    purpose = Column(String(255), nullable=False)
    category = Column(String(100), default="Other", index=True)
    sub_category = Column(String(100), nullable=True)
    merchant_name = Column(String(100), nullable=True, index=True)
    person_name = Column(String(100), nullable=True, index=True)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.UPI)
    payment_provider = Column(String(50), nullable=True)
    external_transaction_id = Column(String(100), nullable=True, index=True)
    reference_number = Column(String(100), nullable=True, index=True)
    transaction_date = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.SUCCESS)
    notes = Column(Text, nullable=True)
    receipt_url = Column(String(255), nullable=True)
    source = Column(Enum(TransactionSource), default=TransactionSource.MANUAL)
    transfer_linked_transaction_id = Column(String(36), nullable=True)
    refund_original_transaction_id = Column(String(36), nullable=True)
    is_flagged_unusual = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")


class PaymentIntent(Base):
    __tablename__ = "payment_intents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    account_id = Column(String(36), ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    purpose = Column(String(255), nullable=False)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.UPI)
    payee_vpa = Column(String(100), nullable=True)
    payee_name = Column(String(100), nullable=True)
    status = Column(Enum(PaymentIntentStatus), default=PaymentIntentStatus.CREATED)
    deep_link_url = Column(Text, nullable=True)
    result_code = Column(String(50), nullable=True)
    result_message = Column(String(255), nullable=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="payment_intents")


class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    payment_intent_id = Column(String(36), ForeignKey("payment_intents.id"), nullable=False)
    provider_name = Column(String(50), nullable=False)
    attempt_timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(PaymentIntentStatus), default=PaymentIntentStatus.INITIATED)
    raw_response = Column(JSON, nullable=True)


class Person(Base):
    __tablename__ = "people"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    upi_id = Column(String(100), nullable=True)
    net_balance = Column(Float, default=0.0) # >0 Ravi owes you, <0 You owe Ravi
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="people")
    iou_entries = relationship("IOUEntry", back_populates="person", cascade="all, delete-orphan")


class IOUEntry(Base):
    __tablename__ = "iou_entries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    person_id = Column(String(36), ForeignKey("people.id"), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    iou_type = Column(String(20), nullable=False) # LENT (You gave) or BORROWED (You took) or SETTLED
    description = Column(String(255), nullable=True)
    due_date = Column(DateTime, nullable=True)
    is_settled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    person = relationship("Person", back_populates="iou_entries")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    category = Column(String(100), nullable=False)
    monthly_limit = Column(Float, nullable=False)
    current_spent = Column(Float, default=0.0)
    month = Column(Integer, nullable=False) # 1-12
    year = Column(Integer, nullable=False)
    status = Column(Enum(BudgetStatus), default=BudgetStatus.NORMAL)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="budgets")


class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_saved = Column(Float, default=0.0)
    target_date = Column(DateTime, nullable=True)
    color = Column(String(20), default="#4CC9F0")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="goals")


class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    frequency = Column(String(20), default="MONTHLY") # DAILY, WEEKLY, MONTHLY, YEARLY
    category = Column(String(100), default="Bills")
    next_due_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recurring")


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    image_url = Column(String(255), nullable=True)
    merchant_name = Column(String(100), nullable=True)
    total_amount = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    receipt_date = Column(DateTime, nullable=True)
    category = Column(String(100), nullable=True)
    items = Column(JSON, default=list) # [{name, price, qty}]
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AIClassification(Base):
    __tablename__ = "ai_classifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    input_text = Column(String(255), nullable=False)
    predicted_category = Column(String(100), nullable=False)
    predicted_subcategory = Column(String(100), nullable=True)
    confidence = Column(Float, default=0.0)
    user_corrected_category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String(100), nullable=False)
    message = Column(String(255), nullable=False)
    notification_type = Column(String(50), default="GENERAL") # BUDGET_ALERT, PAYMENT_SUCCESS, UNUSUAL_EXPENSE, GOAL_PROGRESS
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)
