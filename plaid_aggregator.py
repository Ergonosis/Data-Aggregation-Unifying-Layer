#!/usr/bin/env python3
"""
Plaid local aggregator (sandbox-friendly).

Usage:
  PLAID_CLIENT_ID=... PLAID_SECRET=... PLAID_ENV=sandbox python plaid_aggregator.py
  PLAID_CLIENT_ID=... PLAID_SECRET=... PLAID_ENV=development python plaid_aggregator.py --access-token <token>
"""

import argparse
import json
import os
from datetime import date, timedelta
from typing import Any, Dict, List

import requests


PLAID_ENVS = {
    "sandbox": "https://sandbox.plaid.com",
    "development": "https://development.plaid.com",
    "production": "https://production.plaid.com",
}


def _env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required env var: {name}")
    return value


def plaid_post(base_url: str, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{base_url}{endpoint}"
    resp = requests.post(url, json=payload, timeout=30)
    if resp.status_code >= 400:
        raise SystemExit(f"Plaid error {resp.status_code}: {resp.text}")
    return resp.json()


def sandbox_public_token(
    base_url: str, client_id: str, secret: str, institution_id: str, products: List[str]
) -> str:
    payload = {
        "client_id": client_id,
        "secret": secret,
        "institution_id": institution_id,
        "initial_products": products,
    }
    data = plaid_post(base_url, "/sandbox/public_token/create", payload)
    return data["public_token"]


def exchange_public_token(
    base_url: str, client_id: str, secret: str, public_token: str
) -> str:
    payload = {
        "client_id": client_id,
        "secret": secret,
        "public_token": public_token,
    }
    data = plaid_post(base_url, "/item/public_token/exchange", payload)
    return data["access_token"]


def accounts_get(base_url: str, client_id: str, secret: str, access_token: str) -> Dict[str, Any]:
    payload = {
        "client_id": client_id,
        "secret": secret,
        "access_token": access_token,
    }
    return plaid_post(base_url, "/accounts/get", payload)


def balances_get(base_url: str, client_id: str, secret: str, access_token: str) -> Dict[str, Any]:
    payload = {
        "client_id": client_id,
        "secret": secret,
        "access_token": access_token,
    }
    return plaid_post(base_url, "/accounts/balance/get", payload)


def transactions_get(
    base_url: str,
    client_id: str,
    secret: str,
    access_token: str,
    start_date: str,
    end_date: str,
) -> Dict[str, Any]:
    payload = {
        "client_id": client_id,
        "secret": secret,
        "access_token": access_token,
        "start_date": start_date,
        "end_date": end_date,
    }
    return plaid_post(base_url, "/transactions/get", payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plaid local data puller")
    parser.add_argument("--access-token", help="Use an existing access_token")
    parser.add_argument("--institution-id", default="ins_109508", help="Sandbox institution id")
    parser.add_argument("--days", type=int, default=30, help="Transaction lookback window")
    args = parser.parse_args()

    client_id = _env("PLAID_CLIENT_ID")
    secret = _env("PLAID_SECRET")
    env = os.getenv("PLAID_ENV", "sandbox").strip().lower()
    if env not in PLAID_ENVS:
        raise SystemExit(f"PLAID_ENV must be one of: {', '.join(PLAID_ENVS.keys())}")
    base_url = PLAID_ENVS[env]

    access_token = args.access_token
    if not access_token:
        if env != "sandbox":
            raise SystemExit("In non-sandbox environments, pass --access-token from Link flow.")
        public_token = sandbox_public_token(
            base_url, client_id, secret, args.institution_id, ["transactions"]
        )
        access_token = exchange_public_token(base_url, client_id, secret, public_token)

    today = date.today()
    start_date = (today - timedelta(days=args.days)).isoformat()
    end_date = today.isoformat()

    data = {
        "accounts": accounts_get(base_url, client_id, secret, access_token),
        "balances": balances_get(base_url, client_id, secret, access_token),
        "transactions": transactions_get(
            base_url, client_id, secret, access_token, start_date, end_date
        ),
    }

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
