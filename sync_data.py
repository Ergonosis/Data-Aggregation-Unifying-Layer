import os, json
from dotenv import load_dotenv
from extractors.plaid_ext import PlaidExtractor, fetch_and_store

load_dotenv()

def get_weekly_window_days():
    raw = os.getenv("SYNC_WINDOW_DAYS", "7")
    try:
        days = int(raw)
    except ValueError:
        print(f"Invalid SYNC_WINDOW_DAYS='{raw}', defaulting to 7.")
        return 7
    if days <= 0:
        print(f"Invalid SYNC_WINDOW_DAYS='{raw}', defaulting to 7.")
        return 7
    return days

def sync():
    engine = PlaidExtractor(os.getenv("PLAID_CLIENT_ID"), os.getenv("PLAID_SECRET"), os.getenv("PLAID_ENV"))
    weekly_window_days = get_weekly_window_days()
    
    if not os.path.exists("records/tokens.json"):
        print("No tokens found. Connect an account via app.py first.")
        return

    with open("records/tokens.json", 'r') as f:
        tokens = json.load(f)

    for item_id, access_token in tokens.items():
        print(f"Syncing item: {item_id}")
        file = fetch_and_store(
            engine.client,
            access_token,
            item_id=item_id,
            is_hard_pull=False,
            window_days=weekly_window_days,
        )
        print(f"Created weekly update ({weekly_window_days} day window): {file}")

if __name__ == "__main__":
    sync()
