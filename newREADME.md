# Data Aggregation Unifying Layer

This service provides a centralized interface for pulling financial data from multiple sources: banking institutions via Plaid and email-based transaction/notification data via Microsoft Graph API. It standardizes the retrieval and local storage of JSON records for downstream processing and auditing.

## System Overview

The project is divided into two primary extraction engines:

## Plaid Integration: A Flask-based web flow for linking bank accounts and a script-based exporter for historical transaction data.

- Microsoft Graph Integration: A daemon-style service that authenticates via Azure to extract email bodies (receipts, alerts, etc.) within specific date ranges.

- Data is persisted to the RECORDS_DIR (default: records/) in JSON format.

## Key Features
- Plaid Link Onboarding: OAuth-ready flow to connect thousands of financial institutions.
- Historical Bank Export: Automatic initial pull upon connection + manual range-based exports.
- MS Graph Email Extraction: Automated retrieval of emails from M365 accounts with built-in HTML-to-text cleaning.
- Token Management: Secure local storage of access tokens and item metadata.

## Audit-Ready Storage: Every extraction is timestamped and saved as a flat JSON file for easy ingestion by BI tools or databases.

- Architecture
- Components
- apps.py: Flask server for handling the Plaid Link lifecycle (Token creation & exchange).

extractors/plaid_ext.py: The core logic for paginated Plaid API calls and JSON writing.

run_script.py: Entry point for manual, date-specific bank transaction exports.

automate.py: Basic MS Graph script to fetch raw email data.

test.py: Advanced MS Graph script that includes regex-based HTML cleaning and formatting.

Quick Start
1. Prerequisites
Python 3.10+

Plaid: Client ID and Secret (from Plaid Dashboard)

Microsoft: Azure App Registration with Mail.Read Application permissions, Client ID, Secret, and Tenant ID.

2. Installation
Bash
# Clone the repository and enter the directory
cd Data-Aggregation-Unifying-Layer

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
3. Configuration
Create a .env file in the root directory:

Code snippet
# Plaid Configuration
PLAID_CLIENT_ID=your_plaid_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox
RECORDS_DIR=records

# Microsoft Graph Configuration
MS_CLIENT_ID=your_ms_client_id
MS_CLIENT_SECRET=your_ms_client_secret
MS_TENANT_ID=your_ms_tenant_id
4. Usage
Bank Data (Plaid)
Link an Account: Run python apps.py, navigate to http://localhost:5000, and follow the Link UI.

Manual Export: Edit the dates in run_script.py and run:

Bash
python run_script.py
Email Data (MS Graph)
To extract and clean recent emails (as configured in the script dates):

Bash
python test.py
Output Files
All data is stored in the directory defined by RECORDS_DIR:

tokens.json: Mapping of item_id to Plaid access_token.

items.json: Metadata regarding connected bank institutions.

range_<start>_to_<end>_<id>.json: Transactional data exports.

Console Output: Currently, MS Graph scripts output to the console (edit test.py to redirect to JSON as needed).

Project Structure
Plaintext
Data-Aggregation-Unifying-Layer/
├── apps.py              # Flask: Plaid Onboarding
├── automate.py          # MS Graph: Raw Extraction
├── test.py              # MS Graph: Cleaned Extraction
├── run_script.py        # Plaid: Manual Export
├── index.html           # Plaid: Frontend Link UI
├── requirements.txt     # Dependencies (msal, plaid-python, flask, etc.)
├── extractors/
│   └── plaid_ext.py     # Plaid API Wrapper
└── records/             # Local Data Warehouse (Gitignored)