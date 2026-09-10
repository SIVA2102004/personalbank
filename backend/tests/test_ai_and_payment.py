import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.models import User, Account, AccountType
from app.schemas.schemas import TransactionCreate
from app.services.ledger_engine import LedgerEngine
from app.ai.ai_service import (
    CategorizationService, VoiceParsingService, ReceiptExtractionService, FinancialAssistantService
)
from app.integrations.payment.payment_service import UPIPaymentAdapter, PaymentAdapterFactory

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

def test_ai_categorization_food():
    res = CategorizationService.predict_category("Swiggy", "Dinner order", 450.0)
    assert res["category"] == "Food"
    assert res["sub_category"] == "Food Delivery"
    assert res["confidence"] >= 0.9

def test_ai_categorization_transport():
    res = CategorizationService.predict_category("Uber India", "Ride to office", 320.0)
    assert res["category"] == "Transportation"
    assert res["sub_category"] == "Cab Service"

def test_voice_parsing_service():
    speech = "I paid Ravi 500 rupees for lunch from SBI using UPI"
    parsed = VoiceParsingService.parse_speech_to_transaction(speech)
    assert parsed["understood"] is True
    ext = parsed["extracted"]
    assert ext["amount"] == 500.0
    assert ext["person"] == "Ravi"
    assert ext["purpose"] == "Lunch"
    assert ext["account_hint"] == "SBI"
    assert ext["payment_method"] == "UPI"

def test_receipt_extraction_service():
    receipt = ReceiptExtractionService.process_receipt_image()
    assert receipt["merchant"] == "Reliance Smart Superstore"
    assert receipt["total"] == 1245.50
    assert len(receipt["items"]) > 0

def test_financial_assistant_guardrails(db):
    user = User(id="u1", email="u1@test.com", hashed_password="pw", full_name="User One")
    db.add(user)
    acc = Account(
        user_id=user.id,
        account_name="SBI Savings",
        account_type=AccountType.BANK,
        institution_name="SBI",
        opening_balance=22000.0,
        current_balance=22000.0
    )
    db.add(acc)
    db.commit()

    # Query 1: SBI balance
    res1 = FinancialAssistantService.answer_query(db, user.id, "How much do I have in SBI?")
    assert "22,000" in res1["answer"]

    # Query 2: Missing information guardrail
    res2 = FinancialAssistantService.answer_query(db, user.id, "How much will the stock market rise next week?")
    assert "I don't have enough transaction data" in res2["answer"]

def test_upi_intent_deep_link():
    adapter = PaymentAdapterFactory.get_adapter("UPI")
    res = adapter.initiate_payment(1500.0, "College Books", "INR", {"payee_vpa": "college@sbi", "payee_name": "ABC College"})
    assert "upi://pay?" in res["deep_link"]
    assert "am=1500.00" in res["deep_link"]
    assert "college%40sbi" in res["deep_link"] or "college@sbi" in res["deep_link"]
