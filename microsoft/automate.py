import requests
import msal
from datetime import datetime

# ==========================
# CONFIGURATION
# ==========================
from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env

CLIENT_ID = os.environ["MS_CLIENT_ID"]
CLIENT_SECRET = os.environ["MS_CLIENT_SECRET"]
TENANT_ID = os.environ["MS_TENANT_ID"]

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

USER_EMAIL = "xiaoyangsong@ergonosisdev.onmicrosoft.com"

START_DATE = "2026-01-01T00:00:00Z"
END_DATE   = "2026-02-28T23:59:59Z"

# ==========================
# AUTHENTICATION
# ==========================
app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET,
)

result = app.acquire_token_for_client(scopes=SCOPE)

if "access_token" not in result:
    print(result)
    raise Exception("Could not obtain access token")

access_token = result["access_token"]

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# ==========================
# INITIAL API CALL
# ==========================
filter_query = (
    f"receivedDateTime ge {START_DATE} and "
    f"receivedDateTime le {END_DATE}"
)

url = (
    f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/messages"
    f"?$filter={filter_query}"
    f"&$select=subject,from,toRecipients,receivedDateTime,body"
    f"&$top=50"  # adjust per page
)

while url:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()
    for msg in data.get("value", []):
        print("Subject:", msg.get("subject"))
        print("From:", msg.get("from", {}).get("emailAddress", {}).get("address"))
        print("Received:", msg.get("receivedDateTime"))
        # Print body content
        body = msg.get("body", {})
        if body.get("contentType") == "HTML":
            print("Body (HTML):", body.get("content"), "...")  # first 500 chars
        else:
            print("Body (Text):", body.get("content"), "...")
        print("-" * 80)

    # Pagination support
    url = data.get("@odata.nextLink")  # will be None if no more pages