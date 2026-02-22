import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from datetime import date, timedelta

class PlaidExtractor:
    def __init__(self, client_id, secret, env):
        # Maps environment string to Plaid constants
        host = plaid.Environment.Sandbox
        if env == 'development': host = plaid.Environment.Development
        elif env == 'production': host = plaid.Environment.Production

        configuration = plaid.Configuration(
            host=host,
            api_key={'clientId': client_id, 'secret': secret}
        )
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def get_transactions(self, access_token):
        """Fetches the last 30 days of transactions."""
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )
        response = self.client.transactions_get(request)
        return response.to_dict()