import requests
import msal
import re
from html import unescape

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
headers = {"Authorization": f"Bearer {access_token}"}

# ==========================
# HELPER TO CLEAN HTML
# ==========================
def html_to_text(html):
    text = re.sub(r"<[^>]+>", "", html)   # remove tags
    text = unescape(text)                 # decode HTML entities
    text = re.sub(r"\s+", " ", text)     # collapse whitespace
    return text.strip()

# ==========================
# FETCH EMAILS
# ==========================
filter_query = f"receivedDateTime ge {START_DATE} and receivedDateTime le {END_DATE}"

url = (
    f"https://graph.microsoft.com/v1.0/users/{USER_EMAIL}/messages"
    f"?$filter={filter_query}"
    f"&$select=subject,from,receivedDateTime,body"
    f"&$top=50"
)

while url:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.text)
    data = response.json()

    for msg in data.get("value", []):
        subject = msg.get("subject", "")
        sender = msg.get("from", {}).get("emailAddress", {}).get("address", "")
        received = msg.get("receivedDateTime", "")
        
        # Extract body text only
        body = msg.get("body", {})
        content = body.get("content", "")
        if body.get("contentType") == "HTML":
            content = html_to_text(content)
        
        # Print nicely
        print(f"Subject: {subject}")
        print(f"From: {sender}")
        print(f"Received: {received}")
        print("Message Body:")
        print(content)
        print("="*80)

    url = data.get("@odata.nextLink")