import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.models import User, Account, AccountType, Transaction, TransactionType, TransactionStatus, PaymentMethod
from app.schemas.schemas import TransactionCreate, TransferCreate, RefundCreate
from app.services.ledger_engine import LedgerEngine

# In-memory test db
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db):
    user = User(
        id="user-123",
        email="test@moneyflow.ai",
        hashed_password="dummyhashedpwd",
        full_name="Siva Test",
        preferred_currency="INR"
    )
    db.add(user)
    db.commit()
    return user

def test_financial_case_1_expense_calculation(db, test_user):
    """Opening: ₹10,000; Expense: ₹2,000 -> Expected: ₹8,000"""
    acc = Account(
        user_id=test_user.id,
        account_name="SBI Savings",
        account_type=AccountType.BANK,
        institution_name="SBI",
        opening_balance=10000.0,
        current_balance=10000.0,
        currency="INR"
    )
    db.add(acc)
    db.commit()

    tx_in = TransactionCreate(
        account_id=acc.id,
        transaction_type=TransactionType.DEBIT,
        amount=2000.0,
        purpose="College Books",
        category="Education"
    )
    LedgerEngine.record_transaction(db, test_user.id, tx_in)

    bal = LedgerEngine.recalculate_account_balance(db, acc.id)
    assert bal == 8000.0

def test_financial_case_2_credit_and_expense(db, test_user):
    """Opening: ₹10,000; Credit: ₹5,000; Expense: ₹2,000 -> Expected: ₹13,000"""
    acc = Account(
        user_id=test_user.id,
        account_name="HDFC",
        account_type=AccountType.BANK,
        institution_name="HDFC",
        opening_balance=10000.0,
        current_balance=10000.0,
        currency="INR"
    )
    db.add(acc)
    db.commit()

    # Credit
    LedgerEngine.record_transaction(db, test_user.id, TransactionCreate(
        account_id=acc.id,
        transaction_type=TransactionType.CREDIT,
        amount=5000.0,
        purpose="Salary Bonus",
        category="Salary"
    ))

    # Expense
    LedgerEngine.record_transaction(db, test_user.id, TransactionCreate(
        account_id=acc.id,
        transaction_type=TransactionType.DEBIT,
        amount=2000.0,
        purpose="Dinner",
        category="Food"
    ))

    bal = LedgerEngine.recalculate_account_balance(db, acc.id)
    assert bal == 13000.0

def test_financial_case_3_account_transfer(db, test_user):
    """
    Transfer:
    SBI ₹10,000 -> Transfer ₹3,000 to HDFC (opening ₹0)
    Expected: SBI ₹7,000, HDFC ₹3,000, Total wealth unchanged (₹10,000).
    """
    sbi = Account(
        user_id=test_user.id,
        account_name="SBI",
        account_type=AccountType.BANK,
        institution_name="SBI",
        opening_balance=10000.0,
        current_balance=10000.0,
        currency="INR"
    )
    hdfc = Account(
        user_id=test_user.id,
        account_name="HDFC",
        account_type=AccountType.BANK,
        institution_name="HDFC",
        opening_balance=0.0,
        current_balance=0.0,
        currency="INR"
    )
    db.add_all([sbi, hdfc])
    db.commit()

    transfer = TransferCreate(
        from_account_id=sbi.id,
        to_account_id=hdfc.id,
        amount=3000.0,
        purpose="Fund relocation"
    )
    LedgerEngine.execute_transfer(db, test_user.id, transfer)

    sbi_bal = LedgerEngine.recalculate_account_balance(db, sbi.id)
    hdfc_bal = LedgerEngine.recalculate_account_balance(db, hdfc.id)

    assert sbi_bal == 7000.0
    assert hdfc_bal == 3000.0
    assert (sbi_bal + hdfc_bal) == 10000.0

def test_financial_case_4_refund_reconciliation(db, test_user):
    """Expense ₹1,000, Refund ₹1,000 -> Net expense ₹0"""
    acc = Account(
        user_id=test_user.id,
        account_name="SBI",
        account_type=AccountType.BANK,
        institution_name="SBI",
        opening_balance=5000.0,
        current_balance=5000.0,
        currency="INR"
    )
    db.add(acc)
    db.commit()

    orig_tx = LedgerEngine.record_transaction(db, test_user.id, TransactionCreate(
        account_id=acc.id,
        transaction_type=TransactionType.DEBIT,
        amount=1000.0,
        purpose="Amazon purchase",
        category="Shopping"
    ))
    assert LedgerEngine.recalculate_account_balance(db, acc.id) == 4000.0

    # Refund
    refund = RefundCreate(
        original_transaction_id=orig_tx.id,
        amount=1000.0,
        reason="Returned item"
    )
    LedgerEngine.execute_refund(db, test_user.id, refund)

    assert LedgerEngine.recalculate_account_balance(db, acc.id) == 5000.0

def test_duplicate_transaction_detection(db, test_user):
    acc = Account(
        user_id=test_user.id,
        account_name="Cash",
        account_type=AccountType.CASH,
        institution_name="Cash",
        opening_balance=1000.0,
        current_balance=1000.0,
        currency="INR"
    )
    db.add(acc)
    db.commit()

    LedgerEngine.record_transaction(db, test_user.id, TransactionCreate(
        account_id=acc.id,
        transaction_type=TransactionType.DEBIT,
        amount=500.0,
        purpose="Coffee",
        merchant_name="Starbucks",
        reference_number="TXN-998811"
    ))

    # Test detection with reference number
    dup = LedgerEngine.detect_duplicate(db, test_user.id, acc.id, 500.0, reference_number="TXN-998811")
    assert dup is not None
    assert dup.reference_number == "TXN-998811"
