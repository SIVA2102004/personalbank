# MoneyFlow AI API Documentation

Base URL: `http://localhost:8000/api/v1`

## Standard Envelope
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "error": null
}
```

## Endpoints

### Auth
- `POST /auth/register`: Register user
- `POST /auth/login`: Authenticate and receive JWT
- `GET /auth/me`: Current user profile

### Accounts
- `GET /accounts`: List financial accounts with recalculated balances
- `POST /accounts`: Create new account
- `GET /accounts/{id}`: Account details

### Ledger & Transactions
- `GET /transactions`: List transactions with filters (category, account, type, search)
- `POST /transactions`: Record debit/credit transaction with duplicate & anomaly detection
- `POST /transactions/transfer`: Transfer between accounts (net wealth preserved)
- `POST /transactions/refund`: Reconcile refund linked to original transaction

### Payment Intent
- `POST /payment-intents`: Create intent with purpose, amount, and payment method
- `POST /payment-intents/{id}/confirm`: Mark payment success/failed and commit to ledger

### AI & Assistant
- `POST /ai/assistant`: Factual queries answered strictly from verified ledger
- `POST /ai/categorize`: Predict expense category & subcategory
- `POST /ai/voice-parse`: Convert spoken audio/text into structured payment parameters
- `POST /ai/receipt-scan`: OCR receipt extraction

### Budgets, Goals & People
- `GET /budgets`, `POST /budgets`
- `GET /goals`, `POST /goals`
- `GET /people`, `POST /people`, `POST /people/{id}/iou`