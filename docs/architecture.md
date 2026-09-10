# MoneyFlow AI System Architecture

## Overview
MoneyFlow AI acts as a personal financial ledger, payment intent manager, and AI financial assistant.
It tracks opening & current balances, records payment reasons before initiating transfers, auto-categorizes transactions with AI guardrails, detects anomalies, and supports voice transactions & receipt scanning.

## System Architecture Diagram
```mermaid
graph TD
    Mobile[Flutter Mobile App] --> Gateway[FastAPI Backend]
    Gateway --> Auth[Auth & Security Engine]
    Gateway --> Ledger[Ledger & Balance Engine]
    Gateway --> Payment[Payment Intent State Machine]
    Gateway --> AI[AI Services with Guardrails]
    Ledger --> DB[(PostgreSQL / SQLite)]
    Payment --> Adapters[Payment Adapters: UPI / Mock]
```