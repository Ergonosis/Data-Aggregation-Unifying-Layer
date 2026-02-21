import msal
import requests

class MSGraphExtractor:
    def __init__(self, tenant_id, client_id, client_secret):
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = ["https://graph.microsoft.com/.default"]
        self.app = msal.ConfidentialClientApplication(
            client_id, authority=self.authority, client_credential=self.client_secret
        )

    def fetch_emails(self, user_email):
        result = self.app.acquire_token_for_client(scopes=self.scope)
        if "access_token" not in result:
            raise Exception(f"MS Graph Auth Failed: {result.get('error_description')}")
        
        headers = {'Authorization': f'Bearer {result["access_token"]}'}
        url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages?$top=10"
        response = requests.get(url, headers=headers)
        return response.json()