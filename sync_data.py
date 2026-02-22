import os, json
from dotenv import load_dotenv
from extractors.plaid_ext import PlaidExtractor, fetch_and_store

load_dotenv()

def sync():
    engine = PlaidExtractor(os.getenv("PLAID_CLIENT_ID"), os.getenv("PLAID_SECRET"), os.getenv("PLAID_ENV"))
    
    if not os.path.exists("storage/tokens.json"):
        print("No tokens found. Connect an account via app.py first.")
        return

    with open("storage/tokens.json", 'r') as f:
        tokens = json.load(f)

    for item_id, access_token in tokens.items():
        print(f"Syncing item: {item_id}")
        file = fetch_and_store(engine.client, access_token, is_hard_pull=False)
        print(f"Created weekly update: {file}")

if __name__ == "__main__":
    sync()