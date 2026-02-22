import json
import os
from datetime import date, timedelta
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest

class PlaidExtractor:
    def __init__(self, client_id, secret, env):
        host = plaid.Environment.Sandbox
        if env == 'development': host = plaid.Environment.Development
        elif env == 'production': host = plaid.Environment.Production

        configuration = plaid.Configuration(
            host=host,
            api_key={'clientId': client_id, 'secret': secret}
        )
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

def fetch_and_store(client, access_token, is_hard_pull=False):
    """Automated date logic for Hard Pull vs Weekly Pull."""
    end_date = date.today()
    # 730 days for hard pull (2 years), 7 days for weekly
    start_date = end_date - timedelta(days=(730 if is_hard_pull else 7))
    
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )
    
    response = client.transactions_get(request)
    data = response.to_dict()
    
    # Storage logic
    prefix = "hard_pull" if is_hard_pull else "weekly"
    filename = f"storage/plaid/{prefix}_{end_date}.json"
    os.makedirs("storage/plaid", exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, default=str)
    
    return filename
