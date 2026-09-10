from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field
from app.models.models import AccountType, TransactionType, TransactionStatus, TransactionSource, PaymentMethod, PaymentIntentStatus, BudgetStatus

# Standard API Envelope
class ResponseModel(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[Any] = None

# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    preferred_currency: Optional[str] = "INR"
    country: Optional[str] = "India"
    monthly_income: Optional[float] = 0.0
    financial_goal: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    preferred_currency: str
    country: str
    monthly_income: float
    financial_goal: Optional[str]
    is_active: bool

# Account Schemas
class AccountCreate(BaseModel):
    account_name: str
    account_type: AccountType
    institution_name: str
    masked_identifier: Optional[str] = None
    opening_balance: float = 0.0
    currency: Optional[str] = "INR"
    color: Optional[str] = "#4361EE"
    icon: Optional[str] = "account_balance"

class AccountUpdate(BaseModel):
    account_name: Optional[str] = None
    institution_name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None

class AccountResponse(BaseModel):
    id: str
    user_id: str
    account_name: str
    account_type: AccountType
    institution_name: str
    masked_identifier: Optional[str]
    opening_balance: float
    current_balance: float
    currency: str
    color: str
    icon: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Transaction Schemas
class TransactionCreate(BaseModel):
    account_id: str
    transaction_type: TransactionType = TransactionType.DEBIT
    amount: float = Field(gt=0, description="Amount must be positive")
    purpose: str
    category: Optional[str] = "Other"
    sub_category: Optional[str] = None
    merchant_name: Optional[str] = None
    person_name: Optional[str] = None
    payment_method: Optional[PaymentMethod] = PaymentMethod.UPI
    payment_provider: Optional[str] = None
    external_transaction_id: Optional[str] = None
    reference_number: Optional[str] = None
    transaction_date: Optional[datetime] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    source: Optional[TransactionSource] = TransactionSource.MANUAL

class TransferCreate(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float = Field(gt=0)
    purpose: Optional[str] = "Account Transfer"
    notes: Optional[str] = None

class RefundCreate(BaseModel):
    original_transaction_id: str
    amount: Optional[float] = None
    reason: Optional[str] = "Refund received"

class TransactionResponse(BaseModel):
    id: str
    user_id: str
    account_id: str
    transaction_type: TransactionType
    amount: float
    currency: str
    purpose: str
    category: str
    sub_category: Optional[str]
    merchant_name: Optional[str]
    person_name: Optional[str]
    payment_method: PaymentMethod
    payment_provider: Optional[str]
    external_transaction_id: Optional[str]
    reference_number: Optional[str]
    transaction_date: datetime
    status: TransactionStatus
    notes: Optional[str]
    receipt_url: Optional[str]
    source: TransactionSource
    transfer_linked_transaction_id: Optional[str]
    refund_original_transaction_id: Optional[str]
    is_flagged_unusual: bool
    created_at: datetime

# Payment Intent Schemas
class PaymentIntentCreate(BaseModel):
    account_id: str
    amount: float = Field(gt=0)
    purpose: str
    payment_method: PaymentMethod = PaymentMethod.UPI
    payee_vpa: Optional[str] = None
    payee_name: Optional[str] = None

class PaymentIntentExecuteRequest(BaseModel):
    provider: Optional[str] = "mock_upi"

class PaymentIntentConfirmRequest(BaseModel):
    status: PaymentIntentStatus = PaymentIntentStatus.SUCCESS
    reference_number: Optional[str] = None
    notes: Optional[str] = None

# Person / IOU
class PersonCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    upi_id: Optional[str] = None
    notes: Optional[str] = None

class IOUEntryCreate(BaseModel):
    amount: float = Field(gt=0)
    iou_type: str # LENT, BORROWED, SETTLED
    description: Optional[str] = None
    due_date: Optional[datetime] = None

# Budgets & Goals
class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float = Field(gt=0)
    month: Optional[int] = None
    year: Optional[int] = None

class SavingsGoalCreate(BaseModel):
    name: str
    target_amount: float = Field(gt=0)
    current_saved: Optional[float] = 0.0
    target_date: Optional[datetime] = None
    color: Optional[str] = "#4CC9F0"

class SavingsGoalContribution(BaseModel):
    amount: float = Field(gt=0)
    account_id: Optional[str] = None

# AI & Smart Features
class AICategorizeRequest(BaseModel):
    merchant: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None

class VoiceParseRequest(BaseModel):
    speech_text: str

class ReceiptScanResponse(BaseModel):
    merchant: str
    date: Optional[str] = None
    total: float
    tax: Optional[float] = 0.0
    items: List[dict] = []
    category: str
    payment_method: Optional[str] = None

class AIQueryRequest(BaseModel):
    query: str
