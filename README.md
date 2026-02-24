# Data Aggregation Unifying Layer

This service extracts account transaction data from Plaid and stores the response as local JSON files for downstream processing.

## System Overview

The application provides a simple web flow to connect a Plaid institution and export recent transactions.

- `app.py` hosts a Flask API and serves the frontend.
- `index.html` launches Plaid Link in the browser.
- `extractors/plaid_ext.py` wraps Plaid API access and retrieves transactions.
- Extracted data is written to `RECORDS_DIR` (default `records/`).

## Key Features

- Plaid Link onboarding via `POST /api/create_link_token`.
- Secure token exchange via `POST /api/exchange_public_token`.
- Automatic initial retrieval of full available transaction history after account linking.
- On-demand parameterized export via `POST /api/fetch_date_range`.
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
- `RECORDS_DIR` (default `records/`)
  - Local output location for generated JSON and logs.

### Runtime Flow

1. User opens `http://localhost:5000`.
2. Frontend requests a Plaid `link_token` from `/api/create_link_token`.
3. User completes Plaid Link and frontend receives a `public_token`.
4. Frontend sends `public_token` to `/api/exchange_public_token`.
5. Backend exchanges token, fetches full available history, and saves JSON to `RECORDS_DIR`.
6. User can request additional exports with optional filters from the UI.

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

# Optional defaults for manual exports when start/end are left blank
EXPORT_START_DATE=2026-01-01
EXPORT_END_DATE=2026-01-31

# Optional output directory for tokens, metadata, and JSON exports
RECORDS_DIR=records
```

### 4) Run the application

```bash
python app.py
```

Then open `http://localhost:5000`.

### 5) Validate output

After completing Plaid Link, check your `RECORDS_DIR` (default `records/`) for a file named:

- `full_history_<start_date>_to_<end_date>_<item_id>.json`

To export custom data, use the UI and click `Fetch Date Range`.
All filter fields are optional and treated as "all" when empty.
This creates files named:

- `range_<start_date>_to_<end_date>_<item_id>.json`

Supported filters:

- `start_date`, `end_date` (if omitted, uses `.env` defaults `EXPORT_START_DATE` / `EXPORT_END_DATE`; otherwise full range)
- `item_id` (specific linked bank connection; string or list)
- `financial_institution` (name/id substring, e.g. Chase/Amex; string or list)
- `account_filter` (account id / mask last4 / name substring)
- `include_transactions` (`true`/`false`)
- `include_balances` (`true`/`false`)

Behavior:

- If no `item_id` and no `financial_institution`, exports all linked items.
- If user has Chase and Amex linked, one export call can produce one file per matched item.
- Initial link still performs full available history export for that linked item.

Example single institution:

```json
{
  "financial_institution": "chase",
  "start_date": "2026-02-17",
  "end_date": "2026-02-24"
}
```

Example multiple institutions in one call:

```json
{
  "financial_institution": ["chase", "amex"],
  "start_date": "2026-02-17",
  "end_date": "2026-02-24"
}
```

## Project Structure

```text
Data-Aggregation-Unifying-Layer/
├── README.md
├── app.py
├── index.html
├── requirements.txt
├── setup_weekly_cron.py
├── extractors/
│   ├── __init__.py
│   └── plaid_ext.py
├── records/ (default, can be changed with `RECORDS_DIR`)
└── original/
```

## Notes

- For local testing, use `PLAID_ENV=sandbox`.
- For real users and business data, switch to `PLAID_ENV=development` (or `production` when live) and use the corresponding Plaid credentials for that environment.
- Initial account connect exports full available history using pagination.
- Date-range exports are user-triggered and generated on demand.
