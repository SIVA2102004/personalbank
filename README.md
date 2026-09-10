# MoneyFlow AI — Intelligent Personal Money Management, Payment Tracking & Financial Assistant

> **"Record the reason before you pay, remember exactly what happened afterward."**

MoneyFlow AI is a modern, secure personal finance platform combining an accurate double-entry financial ledger, payment intent management, and an AI financial assistant with strict guardrails.

---

## Key Highlights

- **Payment Intent System**: Record why and to whom you are paying *before* opening UPI or executing the payment.
- **Strict Ledger Mathematics**: Balance = Opening Balance + Total Credits - Total Debits + Adjustments. Transfers between your own accounts preserve net wealth.
- **AI Financial Assistant**: Answers natural language questions exclusively using authorized, verified database transactions. No fabricated numbers.
- **Voice Entry & OCR Receipt Scanning**: Natural language parsing ("I paid Ravi 500 rupees for lunch from SBI using UPI") and simulated multi-item receipt scanning.
- **Zero Banking Credential Storage**: Never stores or requests UPI PINs, ATM PINs, CVVs, or NetBanking passwords.

---

## Project Structure

```text
d:\bank\
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST API endpoints
│   │   ├── core/            # Configuration & Database setup
│   │   ├── models/          # Relational SQL models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Double-entry ledger engine
│   │   ├── integrations/    # Payment adapters (UPI, Mock, etc.)
│   │   ├── ai/              # AI categorization & Assistant guardrails
│   │   └── security/        # JWT & password hashing
│   └── tests/               # Pytest automated test suites
├── mobile/
│   ├── lib/                 # Flutter clean architecture
│   │   ├── core/            # Theme (Light/Dark), Currency Formatter (₹)
│   │   ├── features/        # Home, Auth, Pay, Transactions, Analytics, Voice, OCR, AI
│   │   └── services/        # REST client & API integration
├── database/
│   └── seed/                # Realistic fintech seed data
└── docs/                    # Architecture, API & Security specifications
```

---

## Running the Backend

1. **Start the FastAPI Backend**:
   ```powershell
   cd d:\bank\backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access Interactive API Documentation**:
   - Swagger UI: `http://localhost:8000/api/v1/docs`
   - ReDoc: `http://localhost:8000/api/v1/redoc`

3. **Run Automated Tests**:
   ```powershell
   cd d:\bank
   $env:PYTHONPATH="d:\bank\backend"
   python -m pytest backend/tests -v
   ```

4. **Seed Realistic Demo Data**:
   ```powershell
   cd d:\bank
   $env:PYTHONPATH="d:\bank\backend"
   python database/seed/demo_seed.py
   ```