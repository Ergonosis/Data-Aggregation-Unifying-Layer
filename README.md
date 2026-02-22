# Data Aggregation Unifying Layer

This service extracts account transaction data from Plaid and stores the response as local JSON files for downstream processing.

## System Overview

The application provides a simple web flow to connect a Plaid institution and export recent transactions.

- `app.py` hosts a Flask API and serves the frontend.
- `index.html` launches Plaid Link in the browser.
- `extractors/plaid_ext.py` wraps Plaid API access and retrieves transactions.
- Extracted data is written to `storage/transactions_<item_id>.json`.

## Key Features

- Plaid Link onboarding via `POST /api/create_link_token`.
- Secure token exchange via `POST /api/exchange_public_token`.
- Automatic retrieval of the last 30 days of transactions.
- JSON persistence for auditability and easy handoff to analytics pipelines.
- Minimal modular extractor structure for future source expansion.

## Architecture

### Components

- `app.py`
  - Initializes Flask and Plaid client wiring.
  - Handles token creation, token exchange, and persistence orchestration.
- `extractors/plaid_ext.py`
  - Maps `PLAID_ENV` to the correct Plaid environment.
  - Calls Plaid Transactions API and returns structured response data.
- `index.html`
  - Frontend trigger for Plaid Link and backend API calls.
- `storage/`
  - Local storage location for generated JSON outputs.

### Runtime Flow

1. User opens `http://localhost:5000`.
2. Frontend requests a Plaid `link_token` from `/api/create_link_token`.
3. User completes Plaid Link and frontend receives a `public_token`.
4. Frontend sends `public_token` to `/api/exchange_public_token`.
5. Backend exchanges token, fetches transactions, and saves JSON to `storage/`.

## Quick Start

### Prerequisites

- Python 3.10 or newer
- Plaid credentials

### 1) Create and activate a virtual environment

macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment variables

Create `.env` in the repository root:

```env
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret
PLAID_ENV=sandbox
```

### 4) Run the application

```bash
python app.py
```

Then open `http://localhost:5000`.

### 5) Validate output

After completing Plaid Link, check `storage/` for a file named:

- `transactions_<item_id>.json`

## Project Structure

```text
Data-Aggregation-Unifying-Layer/
├── README.md
├── app.py
├── index.html
├── requirements.txt
├── extractors/
│   ├── __init__.py
│   └── plaid_ext.py
├── storage/
└── original/
```

## Notes

- For local testing, use `PLAID_ENV=sandbox`.
- For real users and business data, switch to `PLAID_ENV=development` (or `production` when live) and use the corresponding Plaid credentials for that environment.
- Transaction extraction currently pulls a rolling 30-day window, defined in `extractors/plaid_ext.py`.
