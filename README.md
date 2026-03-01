# Data Aggregation Unifying Layer

This service pulls account transaction data from Plaid and stores JSON files locally for downstream processing.

## System Overview

The project has two execution paths:

- `apps.py`: Flask app for Plaid Link token creation/exchange and initial full-history pull.
- `run_script.py`: Script-based manual export where you set start/end dates in code.
- Data is written to `RECORDS_DIR` (default: `records`).

## Key Features

- Plaid Link onboarding via `POST /api/create_link_token`.
- Secure token exchange via `POST /api/exchange_public_token`.
- Automatic initial full-history export after account linking.
- Manual date-range exports through `run_script.py`.
- JSON persistence for auditability and easy downstream integration.

## Architecture

### Components

- `apps.py`
  - Initializes Flask and Plaid client wiring.
  - Stores linked account tokens/metadata.
  - Triggers initial historical export for newly linked items.
- `extractors/plaid_ext.py`
  - Wraps Plaid API calls.
  - Handles paginated transaction retrieval.
  - Applies optional account filtering and writes output JSON.
- `run_script.py`
  - Calls `DataExporter.run_export(...)` with explicit dates and optional bank filter.
- `records/`
  - Stores `tokens.json`, `items.json`, and exported data files.

### Runtime Flow

1. Open `http://localhost:5000` and click `Connect Bank`.
2. Frontend requests a Plaid `link_token` from `/api/create_link_token`.
3. Plaid Link returns a `public_token`.
4. Frontend sends `public_token` to `/api/exchange_public_token`.
5. Backend exchanges token, saves credentials/metadata, and writes an initial historical JSON export.
6. Additional exports are run with `run_script.py`.

## Quick Start

### Prerequisites

- Python 3.10+
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

# Output directory for tokens, metadata, and JSON exports
RECORDS_DIR=records

```

### 4) Run Plaid connect app

```bash
python apps.py
```

Then open `http://localhost:5000` and connect an institution.

### 5) Run a manual date-range export

Edit `run_script.py` and set:

- `start_date`
- `end_date`
- optional `bank_filter`

Then run:

```bash
python run_script.py
```

## Output Files

Files are written to `RECORDS_DIR` (default `records/`):

- `tokens.json`: item_id -> access_token
- `items.json`: item metadata (institution info)
- `range_<start>_to_<end>_<item_id>.json`: initial connect export and manual `run_script.py` export

## Project Structure

```text
Data-Aggregation-Unifying-Layer/
├── README.md
├── apps.py
├── index.html
├── run_script.py
├── requirements.txt
├── extractors/
│   ├── __init__.py
│   └── plaid_ext.py
└── records/ (default, configurable with RECORDS_DIR)
```

## Notes

- Use `PLAID_ENV=sandbox` for local testing.
- Switch to `development`/`production` with matching credentials when appropriate.
- Initial account connect exports full available history.
- `run_script.py` is where you define explicit date ranges.
  Data Aggregation Unifying Layer
  This service provides a centralized interface for pulling financial data from multiple sources: banking institutions via Plaid and email-based transaction/notification data via Microsoft Graph API. It standardizes the retrieval and local storage of JSON records for downstream processing and auditing.

System Overview
The project is divided into two primary extraction engines:

Plaid Integration: A Flask-based web flow for linking bank accounts and a script-based exporter for historical transaction data.

Data is written to the RECORDS_DIR (default: records/).

Key Features
Plaid Link Onboarding: OAuth-ready flow to connect financial institutions via /api/create_link_token.

Secure Token Exchange: Backend exchange of public tokens for permanent access tokens.

Flexible Data Export: Support for automatic initial historical pulls and manual date-range exports.

JSON Persistence: All data is stored as local JSON for auditability and easy downstream integration.

Architecture
Components
apps.py: Flask app for Plaid Link lifecycle management (token creation/exchange) and initial historical exports.

extractors/plaid_ext.py: Wraps Plaid API calls, handles paginated transaction retrieval, and manages output formatting.

run_script.py: Entry point for manual, date-range specific bank transaction exports.

records/: Local storage directory for tokens.json, items.json, and all exported data files.

Runtime Flow
Plaid Flow:

Open http://localhost:5000 and click Connect Bank.

Frontend requests a link_token, receives a public_token from Plaid, and exchanges it via the backend.

Backend saves credentials and triggers an initial historical JSON export.

Quick Start

1. Prerequisites
   Python 3.10+

Plaid: Client ID and Secret (from Plaid Dashboard).

2. Installation
   Bash

# macOS/Linux

python -m venv venv
source venv/bin/activate

# Windows

python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies

pip install -r requirements.txt 3) Configure Environment Variables
Create a .env file in the repository root:

Code snippet

# Plaid

PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret
PLAID_ENV=sandbox

# Storage

RECORDS_DIR=records 4) Execution
To start the Plaid connector: python apps.py

To run a manual Plaid export: Edit dates in run_script.py and run python run_script.py.

Output Files
Files are written to RECORDS_DIR (default records/):

tokens.json: item_id -> access_token mapping.

items.json: Linked institution metadata.

range*<start>\_to*<end>\_<id>.json: Exported transaction sets.
