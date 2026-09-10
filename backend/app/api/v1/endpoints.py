from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.core.database import get_db
from app.models.models import (
    User, Account, Transaction, PaymentIntent, PaymentAttempt,
    Person, IOUEntry, Budget, SavingsGoal, RecurringTransaction,
    Notification, AuditLog, TransactionType, TransactionStatus,
    PaymentIntentStatus, PaymentMethod
)
from app.schemas.schemas import (
    ResponseModel, UserRegister, UserLogin, Token, UserResponse,
    AccountCreate, AccountUpdate, AccountResponse,
    TransactionCreate, TransferCreate, RefundCreate, TransactionResponse,
    PaymentIntentCreate, PaymentIntentExecuteRequest, PaymentIntentConfirmRequest,
    PersonCreate, IOUEntryCreate, BudgetCreate, SavingsGoalCreate, SavingsGoalContribution,
    AICategorizeRequest, VoiceParseRequest, ReceiptScanResponse, AIQueryRequest
)
from app.security.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.services.ledger_engine import LedgerEngine
from app.integrations.payment.payment_service import PaymentAdapterFactory
from app.ai.ai_service import (
    CategorizationService, VoiceParsingService, ReceiptExtractionService, FinancialAssistantService
)

api_router = APIRouter()

# --- AUTH ENDPOINTS ---
@api_router.post("/auth/register", response_model=ResponseModel)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        return ResponseModel(success=False, error={"code": "EMAIL_EXISTS", "message": "Email already registered"})
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        preferred_currency=user_in.preferred_currency or "INR",
        country=user_in.country or "India",
        monthly_income=user_in.monthly_income or 0.0,
        financial_goal=user_in.financial_goal
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id})
    return ResponseModel(
        success=True,
        message="Registration successful",
        data={
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "currency": user.preferred_currency
            }
        }
    )

@api_router.post("/auth/login", response_model=ResponseModel)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        return ResponseModel(success=False, error={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"})
    
    token = create_access_token({"sub": user.id})
    return ResponseModel(
        success=True,
        message="Login successful",
        data={
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "currency": user.preferred_currency
            }
        }
    )

@api_router.get("/auth/me", response_model=ResponseModel)
def get_profile(current_user: User = Depends(get_current_user)):
    return ResponseModel(
        success=True,
        data={
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "preferred_currency": current_user.preferred_currency,
            "country": current_user.country,
            "monthly_income": current_user.monthly_income,
            "financial_goal": current_user.financial_goal
        }
    )

# --- ACCOUNTS ENDPOINTS ---
@api_router.get("/accounts", response_model=ResponseModel)
def list_accounts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.user_id == current_user.id, Account.is_active == True).all()
    # Ensure recalculated balances
    res = []
    for acc in accounts:
        bal = LedgerEngine.recalculate_account_balance(db, acc.id)
        res.append({
            "id": acc.id,
            "account_name": acc.account_name,
            "account_type": acc.account_type.value,
            "institution_name": acc.institution_name,
            "masked_identifier": acc.masked_identifier,
            "opening_balance": acc.opening_balance,
            "current_balance": bal,
            "currency": acc.currency,
            "color": acc.color,
            "icon": acc.icon
        })
    return ResponseModel(success=True, data=res)

@api_router.post("/accounts", response_model=ResponseModel)
def create_account(acc_in: AccountCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = Account(
        user_id=current_user.id,
        account_name=acc_in.account_name,
        account_type=acc_in.account_type,
        institution_name=acc_in.institution_name,
        masked_identifier=acc_in.masked_identifier,
        opening_balance=acc_in.opening_balance,
        current_balance=acc_in.opening_balance,
        currency=acc_in.currency or current_user.preferred_currency,
        color=acc_in.color or "#4361EE",
        icon=acc_in.icon or "account_balance"
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return ResponseModel(success=True, message="Account created successfully", data={"id": account.id, "account_name": account.account_name, "balance": account.current_balance})

@api_router.get("/accounts/{account_id}", response_model=ResponseModel)
def get_account_detail(account_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == account_id, Account.user_id == current_user.id).first()
    if not acc:
        return ResponseModel(success=False, error={"code": "NOT_FOUND", "message": "Account not found"})
    bal = LedgerEngine.recalculate_account_balance(db, acc.id)
    return ResponseModel(success=True, data={
        "id": acc.id,
        "account_name": acc.account_name,
        "account_type": acc.account_type.value,
        "institution_name": acc.institution_name,
        "masked_identifier": acc.masked_identifier,
        "opening_balance": acc.opening_balance,
        "current_balance": bal,
        "currency": acc.currency,
        "color": acc.color,
        "icon": acc.icon
    })

# --- TRANSACTIONS & LEDGER ---
@api_router.get("/transactions", response_model=ResponseModel)
def list_transactions(
    category: Optional[str] = None,
    account_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    if category:
        q = q.filter(Transaction.category == category)
    if account_id:
        q = q.filter(Transaction.account_id == account_id)
    if transaction_type:
        q = q.filter(Transaction.transaction_type == transaction_type)
    if search:
        pattern = f"%{search}%"
        q = q.filter((Transaction.purpose.ilike(pattern)) | (Transaction.merchant_name.ilike(pattern)) | (Transaction.person_name.ilike(pattern)))
    
    txs = q.order_by(Transaction.transaction_date.desc()).limit(limit).all()
    data = []
    for t in txs:
        data.append({
            "id": t.id,
            "account_id": t.account_id,
            "account_name": t.account.account_name if t.account else "Unknown",
            "type": t.transaction_type.value,
            "amount": t.amount,
            "currency": t.currency,
            "purpose": t.purpose,
            "category": t.category,
            "sub_category": t.sub_category,
            "merchant_name": t.merchant_name,
            "person_name": t.person_name,
            "payment_method": t.payment_method.value if t.payment_method else "UPI",
            "status": t.status.value if t.status else "SUCCESS",
            "date": str(t.transaction_date),
            "is_flagged_unusual": t.is_flagged_unusual
        })
    return ResponseModel(success=True, data=data)

@api_router.post("/transactions", response_model=ResponseModel)
def create_transaction(tx_in: TransactionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check duplicate
    dup = LedgerEngine.detect_duplicate(
        db, current_user.id, tx_in.account_id, tx_in.amount,
        reference_number=tx_in.reference_number,
        external_id=tx_in.external_transaction_id,
        merchant_name=tx_in.merchant_name
    )
    if dup:
        return ResponseModel(
            success=False,
            error={"code": "DUPLICATE_TRANSACTION", "message": f"Possible duplicate transaction found ({dup.purpose}, ₹{dup.amount})"}
        )

    tx = LedgerEngine.record_transaction(db, current_user.id, tx_in)
    return ResponseModel(
        success=True,
        message="Transaction recorded successfully",
        data={"id": tx.id, "amount": tx.amount, "purpose": tx.purpose, "is_flagged_unusual": tx.is_flagged_unusual}
    )

@api_router.post("/transactions/transfer", response_model=ResponseModel)
def transfer_money(transfer_in: TransferCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        debit_tx, credit_tx = LedgerEngine.execute_transfer(db, current_user.id, transfer_in)
        return ResponseModel(
            success=True,
            message="Transfer completed successfully",
            data={"debit_tx_id": debit_tx.id, "credit_tx_id": credit_tx.id, "amount": transfer_in.amount}
        )
    except ValueError as e:
        return ResponseModel(success=False, error={"code": "TRANSFER_ERROR", "message": str(e)})

@api_router.post("/transactions/refund", response_model=ResponseModel)
def refund_transaction(refund_in: RefundCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        tx = LedgerEngine.execute_refund(db, current_user.id, refund_in)
        return ResponseModel(success=True, message="Refund recorded successfully", data={"id": tx.id, "amount": tx.amount})
    except ValueError as e:
        return ResponseModel(success=False, error={"code": "REFUND_ERROR", "message": str(e)})

# --- PAYMENT INTENT SYSTEM ---
@api_router.post("/payment-intents", response_model=ResponseModel)
def create_payment_intent(intent_in: PaymentIntentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    acc = db.query(Account).filter(Account.id == intent_in.account_id, Account.user_id == current_user.id).first()
    if not acc:
        return ResponseModel(success=False, error={"code": "INVALID_ACCOUNT", "message": "Account not found"})

    intent = PaymentIntent(
        user_id=current_user.id,
        account_id=acc.id,
        amount=intent_in.amount,
        currency=acc.currency,
        purpose=intent_in.purpose,
        payment_method=intent_in.payment_method,
        payee_vpa=intent_in.payee_vpa,
        payee_name=intent_in.payee_name,
        status=PaymentIntentStatus.CREATED
    )
    db.add(intent)
    db.commit()
    db.refresh(intent)

    # Use Adapter
    adapter = PaymentAdapterFactory.get_adapter(intent.payment_method.value)
    init_res = adapter.initiate_payment(
        intent.amount, intent.purpose, intent.currency,
        {"payee_vpa": intent.payee_vpa, "payee_name": intent.payee_name}
    )
    intent.deep_link_url = init_res.get("deep_link")
    intent.status = PaymentIntentStatus.INITIATED
    db.commit()

    return ResponseModel(success=True, message="Payment intent created", data={
        "id": intent.id,
        "amount": intent.amount,
        "purpose": intent.purpose,
        "account_name": acc.account_name,
        "payment_method": intent.payment_method.value,
        "deep_link": intent.deep_link_url,
        "status": intent.status.value
    })

@api_router.post("/payment-intents/{intent_id}/confirm", response_model=ResponseModel)
def confirm_payment_intent(intent_id: str, confirm_in: PaymentIntentConfirmRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    intent = db.query(PaymentIntent).filter(PaymentIntent.id == intent_id, PaymentIntent.user_id == current_user.id).first()
    if not intent:
        return ResponseModel(success=False, error={"code": "NOT_FOUND", "message": "Payment intent not found"})

    intent.status = confirm_in.status
    if confirm_in.status == PaymentIntentStatus.SUCCESS:
        # Create finalized ledger transaction
        tx_in = TransactionCreate(
            account_id=intent.account_id,
            transaction_type=TransactionType.DEBIT,
            amount=intent.amount,
            purpose=intent.purpose,
            category=CategorizationService.predict_category(intent.payee_name, intent.purpose, intent.amount)["category"],
            merchant_name=intent.payee_name,
            payment_method=intent.payment_method,
            reference_number=confirm_in.reference_number,
            notes=confirm_in.notes,
            source=TransactionSource.PAYMENT_FLOW
        )
        tx = LedgerEngine.record_transaction(db, current_user.id, tx_in)
        intent.transaction_id = tx.id
    
    db.commit()
    return ResponseModel(success=True, message=f"Payment marked as {intent.status.value}", data={"intent_id": intent.id, "status": intent.status.value})

# --- DASHBOARD & ANALYTICS ---
@api_router.get("/dashboard", response_model=ResponseModel)
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.user_id == current_user.id, Account.is_active == True).all()
    total_balance = sum([LedgerEngine.recalculate_account_balance(db, a.id) for a in accounts])

    now = datetime.utcnow()
    first_day = datetime(now.year, now.month, 1)

    month_income = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.CREDIT,
        Transaction.status == TransactionStatus.SUCCESS,
        Transaction.transaction_date >= first_day
    ).scalar()

    month_expense = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.DEBIT,
        Transaction.status == TransactionStatus.SUCCESS,
        Transaction.transaction_date >= first_day
    ).scalar()

    remaining = month_income - month_expense

    recent_txs = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.transaction_date.desc()).limit(5).all()

    return ResponseModel(success=True, data={
        "total_balance": round(total_balance, 2),
        "month_income": round(month_income, 2),
        "month_expense": round(month_expense, 2),
        "remaining": round(remaining, 2),
        "accounts": [{"id": a.id, "name": a.account_name, "balance": a.current_balance, "color": a.color} for a in accounts],
        "recent_transactions": [{
            "id": t.id,
            "purpose": t.purpose,
            "amount": t.amount,
            "type": t.transaction_type.value,
            "date": str(t.transaction_date)
        } for t in recent_txs]
    })

@api_router.get("/analytics/summary", response_model=ResponseModel)
def get_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Spending by category
    category_spending = db.query(
        Transaction.category, func.coalesce(func.sum(Transaction.amount), 0.0)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.DEBIT,
        Transaction.status == TransactionStatus.SUCCESS
    ).group_by(Transaction.category).all()

    # Payment methods breakdown
    methods = db.query(
        Transaction.payment_method, func.coalesce(func.sum(Transaction.amount), 0.0)
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_type == TransactionType.DEBIT,
        Transaction.status == TransactionStatus.SUCCESS
    ).group_by(Transaction.payment_method).all()

    return ResponseModel(success=True, data={
        "category_spending": [{"category": c, "amount": round(a, 2)} for c, a in category_spending],
        "payment_methods": [{"method": m.value if m else "OTHER", "amount": round(a, 2)} for m, a in methods]
    })

# --- PEOPLE & IOU ---
@api_router.get("/people", response_model=ResponseModel)
def list_people(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    people = db.query(Person).filter(Person.user_id == current_user.id).all()
    return ResponseModel(success=True, data=[{
        "id": p.id,
        "name": p.name,
        "phone": p.phone,
        "upi_id": p.upi_id,
        "net_balance": p.net_balance
    } for p in people])

@api_router.post("/people", response_model=ResponseModel)
def add_person(person_in: PersonCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    person = Person(
        user_id=current_user.id,
        name=person_in.name,
        phone=person_in.phone,
        upi_id=person_in.upi_id,
        notes=person_in.notes
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return ResponseModel(success=True, message="Person added", data={"id": person.id, "name": person.name})

@api_router.post("/people/{person_id}/iou", response_model=ResponseModel)
def add_iou_entry(person_id: str, iou_in: IOUEntryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id, Person.user_id == current_user.id).first()
    if not person:
        return ResponseModel(success=False, error={"code": "NOT_FOUND", "message": "Person not found"})

    entry = IOUEntry(
        person_id=person.id,
        amount=iou_in.amount,
        iou_type=iou_in.iou_type.upper(),
        description=iou_in.description,
        due_date=iou_in.due_date
    )
    db.add(entry)

    # Net balance calculation: LENT increases what they owe you (+), BORROWED increases what you owe them (-)
    if iou_in.iou_type.upper() == "LENT":
        person.net_balance += iou_in.amount
    elif iou_in.iou_type.upper() == "BORROWED":
        person.net_balance -= iou_in.amount
    elif iou_in.iou_type.upper() == "SETTLED":
        person.net_balance = 0.0

    db.commit()
    return ResponseModel(success=True, message="IOU entry recorded", data={"person": person.name, "net_balance": person.net_balance})

# --- BUDGETS & GOALS ---
@api_router.get("/budgets", response_model=ResponseModel)
def get_budgets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.utcnow()
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id, Budget.month == now.month, Budget.year == now.year).all()
    return ResponseModel(success=True, data=[{
        "id": b.id,
        "category": b.category,
        "monthly_limit": b.monthly_limit,
        "current_spent": b.current_spent,
        "remaining": max(0.0, b.monthly_limit - b.current_spent),
        "status": b.status.value
    } for b in budgets])

@api_router.post("/budgets", response_model=ResponseModel)
def set_budget(budget_in: BudgetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    now = datetime.utcnow()
    m = budget_in.month or now.month
    y = budget_in.year or now.year
    budget = db.query(Budget).filter(Budget.user_id == current_user.id, Budget.category == budget_in.category, Budget.month == m, Budget.year == y).first()
    if not budget:
        budget = Budget(user_id=current_user.id, category=budget_in.category, monthly_limit=budget_in.monthly_limit, month=m, year=y)
        db.add(budget)
    else:
        budget.monthly_limit = budget_in.monthly_limit
    db.commit()
    return ResponseModel(success=True, message="Budget saved")

@api_router.get("/goals", response_model=ResponseModel)
def list_goals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == current_user.id).all()
    return ResponseModel(success=True, data=[{
        "id": g.id,
        "name": g.name,
        "target_amount": g.target_amount,
        "current_saved": g.current_saved,
        "progress_pct": round((g.current_saved / g.target_amount * 100.0), 1) if g.target_amount > 0 else 0,
        "remaining": max(0.0, g.target_amount - g.current_saved)
    } for g in goals])

@api_router.post("/goals", response_model=ResponseModel)
def create_goal(goal_in: SavingsGoalCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = SavingsGoal(
        user_id=current_user.id,
        name=goal_in.name,
        target_amount=goal_in.target_amount,
        current_saved=goal_in.current_saved or 0.0,
        target_date=goal_in.target_date,
        color=goal_in.color or "#4CC9F0"
    )
    db.add(goal)
    db.commit()
    return ResponseModel(success=True, message="Savings goal created", data={"id": goal.id, "name": goal.name})

# --- AI, VOICE & OCR ---
@api_router.post("/ai/categorize", response_model=ResponseModel)
def categorize_tx(req: AICategorizeRequest):
    res = CategorizationService.predict_category(req.merchant, req.description, req.amount)
    return ResponseModel(success=True, data=res)

@api_router.post("/ai/voice-parse", response_model=ResponseModel)
def parse_voice(req: VoiceParseRequest):
    res = VoiceParsingService.parse_speech_to_transaction(req.speech_text)
    return ResponseModel(success=True, data=res)

@api_router.post("/ai/receipt-scan", response_model=ResponseModel)
def scan_receipt():
    res = ReceiptExtractionService.process_receipt_image()
    return ResponseModel(success=True, data=res)

@api_router.post("/ai/assistant", response_model=ResponseModel)
def ask_assistant(req: AIQueryRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    res = FinancialAssistantService.answer_query(db, current_user.id, req.query)
    return ResponseModel(success=True, data=res)
