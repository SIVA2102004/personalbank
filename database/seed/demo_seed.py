from datetime import datetime, timedelta
from app.core.database import SessionLocal, Base, engine
from app.models.models import (
    User, Account, AccountType, Transaction, TransactionType, 
    TransactionStatus, PaymentMethod, Budget, SavingsGoal, Person, IOUEntry
)
from app.security.auth import get_password_hash

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if demo user already exists
    existing = db.query(User).filter(User.email == "demo@moneyflow.ai").first()
    if existing:
        print("Demo data already seeded!")
        db.close()
        return

    print("Seeding realistic fintech demo data...")

    user = User(
        id="demo-user-1",
        email="demo@moneyflow.ai",
        hashed_password=get_password_hash("MoneyFlow@2026"),
        full_name="Siva",
        preferred_currency="INR",
        country="India",
        monthly_income=65000.0,
        financial_goal="Emergency fund of ₹2,00,000 and new laptop"
    )
    db.add(user)
    db.commit()

    # Accounts
    sbi = Account(
        user_id=user.id,
        account_name="SBI Savings",
        account_type=AccountType.BANK,
        institution_name="SBI",
        masked_identifier="••4589",
        opening_balance=25000.0,
        current_balance=22000.0,
        currency="INR",
        color="#2E7D32"
    )
    hdfc = Account(
        user_id=user.id,
        account_name="HDFC Salary",
        account_type=AccountType.BANK,
        institution_name="HDFC Bank",
        masked_identifier="••1024",
        opening_balance=15000.0,
        current_balance=12500.0,
        currency="INR",
        color="#1565C0"
    )
    cash = Account(
        user_id=user.id,
        account_name="Cash Wallet",
        account_type=AccountType.CASH,
        institution_name="Cash",
        opening_balance=3000.0,
        current_balance=3000.0,
        currency="INR",
        color="#EF6C00"
    )
    wallet = Account(
        user_id=user.id,
        account_name="Paytm Wallet",
        account_type=AccountType.WALLET,
        institution_name="Paytm",
        opening_balance=2000.0,
        current_balance=2000.0,
        currency="INR",
        color="#00838F"
    )
    db.add_all([sbi, hdfc, cash, wallet])
    db.commit()

    now = datetime.utcnow()

    # Transactions
    txs = [
        Transaction(
            user_id=user.id, account_id=hdfc.id, transaction_type=TransactionType.CREDIT,
            amount=35000.0, currency="INR", purpose="Monthly Salary", category="Salary",
            merchant_name="Tech Solutions Ltd", payment_method=PaymentMethod.BANK_TRANSFER,
            status=TransactionStatus.SUCCESS, transaction_date=now - timedelta(days=9)
        ),
        Transaction(
            user_id=user.id, account_id=sbi.id, transaction_type=TransactionType.DEBIT,
            amount=5000.0, currency="INR", purpose="College Fees", category="Education",
            merchant_name="Engineering College", payment_method=PaymentMethod.UPI,
            status=TransactionStatus.SUCCESS, transaction_date=now - timedelta(days=7)
        ),
        Transaction(
            user_id=user.id, account_id=sbi.id, transaction_type=TransactionType.DEBIT,
            amount=850.0, currency="INR", purpose="Dinner with friends", category="Food",
            sub_category="Food Delivery", merchant_name="Swiggy", payment_method=PaymentMethod.UPI,
            status=TransactionStatus.SUCCESS, transaction_date=now - timedelta(days=4)
        ),
        Transaction(
            user_id=user.id, account_id=hdfc.id, transaction_type=TransactionType.DEBIT,
            amount=450.0, currency="INR", purpose="Uber Ride to Campus", category="Transportation",
            merchant_name="Uber India", payment_method=PaymentMethod.UPI,
            status=TransactionStatus.SUCCESS, transaction_date=now - timedelta(days=3)
        ),
        Transaction(
            user_id=user.id, account_id=sbi.id, transaction_type=TransactionType.DEBIT,
            amount=1500.0, currency="INR", purpose="College Books", category="Education",
            merchant_name="Sapna Book House", payment_method=PaymentMethod.UPI,
            status=TransactionStatus.SUCCESS, transaction_date=now - timedelta(days=2)
        ),
        Transaction(
            user_id=user.id, account_id=sbi.id, transaction_type=TransactionType.DEBIT,
            amount=500.0, currency="INR", purpose="Lunch with Ravi", category="Food",
            person_name="Ravi", payment_method=PaymentMethod.UPI,
            status=TransactionStatus.SUCCESS, transaction_date=now - timedelta(days=1)
        ),
        Transaction(
            user_id=user.id, account_id=hdfc.id, transaction_type=TransactionType.CREDIT,
            amount=1000.0, currency="INR", purpose="Amazon Refund", category="Shopping",
            merchant_name="Amazon", payment_method=PaymentMethod.UPI,
            status=TransactionStatus.SUCCESS, transaction_date=now - timedelta(hours=12)
        )
    ]
    db.add_all(txs)

    # Budgets
    b1 = Budget(user_id=user.id, category="Food", monthly_limit=5000.0, current_spent=3800.0, month=now.month, year=now.year)
    b2 = Budget(user_id=user.id, category="Transportation", monthly_limit=3000.0, current_spent=1200.0, month=now.month, year=now.year)
    b3 = Budget(user_id=user.id, category="Education", monthly_limit=10000.0, current_spent=6500.0, month=now.month, year=now.year)
    db.add_all([b1, b2, b3])

    # Savings Goals
    g1 = SavingsGoal(user_id=user.id, name="New Laptop", target_amount=60000.0, current_saved=25000.0, target_date=now + timedelta(days=90))
    g2 = SavingsGoal(user_id=user.id, name="Emergency Fund", target_amount=100000.0, current_saved=40000.0, target_date=now + timedelta(days=180))
    db.add_all([g1, g2])

    # People & IOUs
    ravi = Person(user_id=user.id, name="Ravi", phone="+91 9876543210", upi_id="ravi@okaxis", net_balance=2000.0, notes="Roommate")
    priya = Person(user_id=user.id, name="Priya", phone="+91 9123456780", upi_id="priya@okhdfc", net_balance=-800.0, notes="Classmate")
    db.add_all([ravi, priya])
    db.commit()

    db.add(IOUEntry(person_id=ravi.id, amount=2500.0, iou_type="LENT", description="Shared Grocery and Wifi bill"))
    db.add(IOUEntry(person_id=ravi.id, amount=500.0, iou_type="BORROWED", description="Ravi paid for lunch"))
    db.add(IOUEntry(person_id=priya.id, amount=800.0, iou_type="BORROWED", description="Priya bought group project printouts"))

    db.commit()
    db.close()
    print("Demo data successfully populated!")

if __name__ == "__main__":
    seed()
