import uuid
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import (
    Account, Transaction, TransactionType, TransactionStatus, 
    TransactionSource, PaymentMethod, AuditLog, Budget, BudgetStatus, Notification
)
from app.schemas.schemas import TransactionCreate, TransferCreate, RefundCreate

class LedgerEngine:
    @staticmethod
    def recalculate_account_balance(db: Session, account_id: str) -> float:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise ValueError("Account not found")

        total_credits = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
            Transaction.account_id == account_id,
            Transaction.status == TransactionStatus.SUCCESS,
            Transaction.transaction_type.in_([TransactionType.CREDIT, TransactionType.REFUND])
        ).scalar() or 0.0

        total_debits = db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter(
            Transaction.account_id == account_id,
            Transaction.status == TransactionStatus.SUCCESS,
            Transaction.transaction_type == TransactionType.DEBIT
        ).scalar() or 0.0

        current_balance = round(account.opening_balance + total_credits - total_debits, 2)
        account.current_balance = current_balance
        account.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(account)
        return current_balance

    @staticmethod
    def detect_duplicate(
        db: Session,
        user_id: str,
        account_id: str,
        amount: float,
        reference_number: Optional[str] = None,
        external_id: Optional[str] = None,
        merchant_name: Optional[str] = None,
        time_window_minutes: int = 30
    ) -> Optional[Transaction]:
        if external_id:
            dup = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.external_transaction_id == external_id
            ).first()
            if dup:
                return dup

        if reference_number:
            dup = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.reference_number == reference_number
            ).first()
            if dup:
                return dup

        recent_txs = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.account_id == account_id,
            Transaction.amount == amount
        ).order_by(Transaction.created_at.desc()).limit(10).all()

        now = datetime.utcnow()
        for tx in recent_txs:
            diff = (now - tx.created_at).total_seconds() / 60.0
            if diff <= time_window_minutes:
                if merchant_name and tx.merchant_name:
                    if merchant_name.strip().lower() == tx.merchant_name.strip().lower():
                        return tx
                else:
                    return tx

        return None

    @staticmethod
    def check_unusual_spending(
        db: Session,
        user_id: str,
        category: str,
        amount: float
    ) -> bool:
        avg_amount = db.query(func.avg(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.category == category,
            Transaction.transaction_type == TransactionType.DEBIT
        ).scalar()

        if avg_amount and avg_amount > 0:
            if amount >= (avg_amount * 3.0) and amount > 1000:
                return True
        return False

    @classmethod
    def record_transaction(
        cls,
        db: Session,
        user_id: str,
        tx_data: TransactionCreate,
        status: TransactionStatus = TransactionStatus.SUCCESS
    ) -> Transaction:
        account = db.query(Account).filter(Account.id == tx_data.account_id, Account.user_id == user_id).first()
        if not account:
            raise ValueError("Invalid account for user")

        is_unusual = False
        if tx_data.transaction_type == TransactionType.DEBIT:
            is_unusual = cls.check_unusual_spending(db, user_id, tx_data.category or "Other", tx_data.amount)

        tx = Transaction(
            user_id=user_id,
            account_id=tx_data.account_id,
            transaction_type=tx_data.transaction_type,
            amount=round(tx_data.amount, 2),
            currency=account.currency,
            purpose=tx_data.purpose,
            category=tx_data.category or "Other",
            sub_category=tx_data.sub_category,
            merchant_name=tx_data.merchant_name,
            person_name=tx_data.person_name,
            payment_method=tx_data.payment_method or PaymentMethod.UPI,
            payment_provider=tx_data.payment_provider,
            external_transaction_id=tx_data.external_transaction_id,
            reference_number=tx_data.reference_number,
            transaction_date=tx_data.transaction_date or datetime.utcnow(),
            status=status,
            notes=tx_data.notes,
            receipt_url=tx_data.receipt_url,
            source=tx_data.source or TransactionSource.MANUAL,
            is_flagged_unusual=is_unusual
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)

        # Audit Log
        audit = AuditLog(
            user_id=user_id,
            action="TRANSACTION_RECORDED",
            entity_type="TRANSACTION",
            entity_id=tx.id,
            details={"amount": tx.amount, "type": tx.transaction_type.value, "account": account.account_name}
        )
        db.add(audit)

        if is_unusual:
            notif = Notification(
                user_id=user_id,
                title="Unusual Transaction Detected",
                message=f"A payment of {account.currency} {tx.amount} in {tx.category} is significantly higher than your normal spending.",
                notification_type="UNUSUAL_EXPENSE"
            )
            db.add(notif)

        if status == TransactionStatus.SUCCESS:
            cls.recalculate_account_balance(db, account.id)

        if tx.transaction_type == TransactionType.DEBIT and tx.status == TransactionStatus.SUCCESS:
            cls.update_budget_progress(db, user_id, tx.category, tx.amount)

        db.commit()
        return tx

    @classmethod
    def execute_transfer(
        cls,
        db: Session,
        user_id: str,
        transfer: TransferCreate
    ) -> Tuple[Transaction, Transaction]:
        from_acc = db.query(Account).filter(Account.id == transfer.from_account_id, Account.user_id == user_id).first()
        to_acc = db.query(Account).filter(Account.id == transfer.to_account_id, Account.user_id == user_id).first()

        if not from_acc or not to_acc:
            raise ValueError("Source or destination account invalid")
        if from_acc.id == to_acc.id:
            raise ValueError("Cannot transfer to the same account")

        transfer_pair_id = str(uuid.uuid4())

        debit_tx = Transaction(
            user_id=user_id,
            account_id=from_acc.id,
            transaction_type=TransactionType.DEBIT,
            amount=round(transfer.amount, 2),
            currency=from_acc.currency,
            purpose=f"Transfer to {to_acc.account_name}: {transfer.purpose}",
            category="Transfer",
            payment_method=PaymentMethod.BANK_TRANSFER,
            status=TransactionStatus.SUCCESS,
            notes=transfer.notes,
            source=TransactionSource.MANUAL,
            transfer_linked_transaction_id=transfer_pair_id
        )
        db.add(debit_tx)

        credit_tx = Transaction(
            user_id=user_id,
            account_id=to_acc.id,
            transaction_type=TransactionType.CREDIT,
            amount=round(transfer.amount, 2),
            currency=to_acc.currency,
            purpose=f"Transfer from {from_acc.account_name}: {transfer.purpose}",
            category="Transfer",
            payment_method=PaymentMethod.BANK_TRANSFER,
            status=TransactionStatus.SUCCESS,
            notes=transfer.notes,
            source=TransactionSource.MANUAL,
            transfer_linked_transaction_id=transfer_pair_id
        )
        db.add(credit_tx)
        db.commit()

        cls.recalculate_account_balance(db, from_acc.id)
        cls.recalculate_account_balance(db, to_acc.id)

        audit = AuditLog(
            user_id=user_id,
            action="ACCOUNT_TRANSFER",
            entity_type="TRANSFER",
            entity_id=transfer_pair_id,
            details={"from": from_acc.account_name, "to": to_acc.account_name, "amount": transfer.amount}
        )
        db.add(audit)
        db.commit()

        return debit_tx, credit_tx

    @classmethod
    def execute_refund(
        cls,
        db: Session,
        user_id: str,
        refund_data: RefundCreate
    ) -> Transaction:
        orig = db.query(Transaction).filter(
            Transaction.id == refund_data.original_transaction_id,
            Transaction.user_id == user_id
        ).first()

        if not orig:
            raise ValueError("Original transaction not found")

        refund_amount = refund_data.amount if refund_data.amount else orig.amount
        if refund_amount <= 0 or refund_amount > orig.amount:
            raise ValueError(f"Refund amount cannot exceed original amount of {orig.amount}")

        refund_tx = Transaction(
            user_id=user_id,
            account_id=orig.account_id,
            transaction_type=TransactionType.REFUND,
            amount=round(refund_amount, 2),
            currency=orig.currency,
            purpose=f"Refund: {orig.purpose} ({refund_data.reason})",
            category=orig.category,
            sub_category=orig.sub_category,
            merchant_name=orig.merchant_name,
            payment_method=orig.payment_method,
            status=TransactionStatus.SUCCESS,
            source=TransactionSource.MANUAL,
            refund_original_transaction_id=orig.id
        )
        db.add(refund_tx)
        db.commit()

        cls.recalculate_account_balance(db, orig.account_id)
        return refund_tx

    @staticmethod
    def update_budget_progress(db: Session, user_id: str, category: str, amount: float):
        now = datetime.utcnow()
        budget = db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.category == category,
            Budget.month == now.month,
            Budget.year == now.year
        ).first()

        if budget:
            budget.current_spent = round(budget.current_spent + amount, 2)
            pct = (budget.current_spent / budget.monthly_limit) * 100.0 if budget.monthly_limit > 0 else 0
            if pct >= 100:
                budget.status = BudgetStatus.EXCEEDED
                db.add(Notification(
                    user_id=user_id,
                    title="Budget Exceeded!",
                    message=f"You have exceeded your monthly budget for {category} ({budget.current_spent}/{budget.monthly_limit}).",
                    notification_type="BUDGET_ALERT"
                ))
            elif pct >= 80:
                budget.status = BudgetStatus.WARNING
                db.add(Notification(
                    user_id=user_id,
                    title="Budget Warning",
                    message=f"You have spent {round(pct)}% of your monthly budget for {category}.",
                    notification_type="BUDGET_ALERT"
                ))
            db.commit()
