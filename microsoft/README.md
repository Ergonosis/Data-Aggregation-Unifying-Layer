# Microsoft Graph Email Client

Python module for retrieving emails from Microsoft 365 via Microsoft Graph API using **client credentials authentication**. Note that we require credentials in this implementation, instead of OAuth-style authentications.

- ✅ **Single function call interface**
- ✅ Fully parameterized
- ✅ Secure (no hardcoded credentials)
- ✅ Structured return format (`List[Dict]`)
- ✅ Optional HTML → clean text conversion
- ✅ Production-ready module design

---

## Installation & Environment Variables

In your existing Conda or Venv environment, install the following packages:

```bash
pip install requests msal beautifulsoup4 lxml python-dotenv
```

Create a `.env` file in your project root folder like the following:

```
MS_CLIENT_ID=your_client_id
MS_CLIENT_SECRET=your_client_secret
MS_TENANT_ID=your_tenant_id
USER_EMAIL=user@company.com
```

These values correspond to your Azure App Registration configuration.

## Quick Start (Single Function Call)

### `fetch_user_emails(...)`

This is the single public entry point for retrieving emails. Most users only need this function to get started, making the module easy to use. Authentication, token handling, pagination, or message normalization are handled internally.

```
from ms_graph_email_client import fetch_user_emails
from dotenv import load_dotenv
import os

load_dotenv()

emails = fetch_user_emails(
    client_id=os.environ["MS_CLIENT_ID"],
    client_secret=os.environ["MS_CLIENT_SECRET"],
    tenant_id=os.environ["MS_TENANT_ID"],
    user_email=os.environ["USER_EMAIL"],
    start_datetime="2026-01-01T00:00:00Z",
    end_datetime="2026-02-28T23:59:59Z",
    strip_html=True,  # True → return clean visible text only
)

# Example print
# print(emails[0])
```

| Parameter        | Type   | Required | Description                                                                                       |
| ---------------- | ------ | -------- | ------------------------------------------------------------------------------------------------- |
| `client_id`      | `str`  | Yes      | Azure App Registration client ID                                                                  |
| `client_secret`  | `str`  | Yes      | Azure App client secret                                                                           |
| `tenant_id`      | `str`  | Yes      | Azure tenant ID                                                                                   |
| `user_email`     | `str`  | Yes      | Mailbox email address to query                                                                    |
| `start_datetime` | `str`  | Yes      | Start of time range (ISO 8601 UTC format, e.g. `"2026-01-01T00:00:00Z"`)                          |
| `end_datetime`   | `str`  | Yes      | End of time range (ISO 8601 UTC format)                                                           |
| `strip_html`     | `bool` | No       | If `True`, returns clean visible text only. If `False`, returns raw HTML body. Default is `True`. |

### Return Values

Each email is returned as a structured dictionary containing:

- `subject`: email subject title.
- `from`: email sender.
- `to`: a list of receipients.
- `received_datetime`: timestamp.
- `body`: email context.
- `body_content_type`: type of body content.
