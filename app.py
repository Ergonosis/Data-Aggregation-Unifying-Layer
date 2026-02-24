import os, json
from datetime import date
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from extractors.plaid_ext import PlaidExtractor, fetch_and_store

load_dotenv()
app = Flask(__name__)

plaid_engine = PlaidExtractor(os.getenv("PLAID_CLIENT_ID"), os.getenv("PLAID_SECRET"), os.getenv("PLAID_ENV"))

def save_token(item_id, access_token):
    path = "records/tokens.json"
    os.makedirs("records", exist_ok=True)
    tokens = {}
    if os.path.exists(path):
        with open(path, 'r') as f: tokens = json.load(f)
    tokens[item_id] = access_token
    with open(path, 'w') as f: json.dump(tokens, f)

def save_item_metadata(item_id, institution_id=None, institution_name=None):
    path = "records/items.json"
    os.makedirs("records", exist_ok=True)
    items = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            items = json.load(f)
    items[item_id] = {
        "item_id": item_id,
        "institution_id": institution_id,
        "institution_name": institution_name,
    }
    with open(path, "w") as f:
        json.dump(items, f)

def load_tokens():
    path = "records/tokens.json"
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def load_item_metadata():
    path = "records/items.json"
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def str_to_bool(value, default=True):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return default

def normalize_str_or_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    return [text] if text else []

def resolve_item_metadata(client, access_token):
    institution_id = None
    institution_name = None
    try:
        from plaid.model.item_get_request import ItemGetRequest
        item_resp = client.item_get(ItemGetRequest(access_token=access_token)).to_dict()
        institution_id = item_resp.get("item", {}).get("institution_id")
    except Exception:
        institution_id = None

    if not institution_id:
        return None, None

    try:
        from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
        from plaid.model.country_code import CountryCode
        inst_resp = client.institutions_get_by_id(
            InstitutionsGetByIdRequest(
                institution_id=institution_id,
                country_codes=[CountryCode("US")],
            )
        ).to_dict()
        institution_name = inst_resp.get("institution", {}).get("name")
    except Exception:
        institution_name = None
    return institution_id, institution_name

@app.route('/')
def index():
    return render_template_string(open('index.html').read())

@app.route('/api/create_link_token', methods=['POST'])
def link_token():
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.products import Products
    from plaid.model.country_code import CountryCode

    req = LinkTokenCreateRequest(
        products=[Products('transactions')],
        client_name="Data Aggregator",
        country_codes=[CountryCode('US')],
        language='en',
        user=LinkTokenCreateRequestUser(client_user_id='user_1')
    )
    return jsonify(plaid_engine.client.link_token_create(req).to_dict())

@app.route('/api/exchange_public_token', methods=['POST'])
def exchange():
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
    pub_token = request.json.get('public_token')
    exchange_resp = plaid_engine.client.item_public_token_exchange(ItemPublicTokenExchangeRequest(public_token=pub_token))
    
    access_token = exchange_resp['access_token']
    item_id = exchange_resp["item_id"]
    save_token(item_id, access_token)
    institution_id, institution_name = resolve_item_metadata(plaid_engine.client, access_token)
    save_item_metadata(item_id, institution_id, institution_name)
    
    # Immediate full available history pull
    file = fetch_and_store(
        plaid_engine.client,
        access_token,
        item_id=item_id,
        is_hard_pull=True,
    )
    return jsonify(
        {
            "status": "Token saved & full history pull complete",
            "item_id": item_id,
            "institution_id": institution_id,
            "institution_name": institution_name,
            "file": file,
        }
    )

@app.route('/api/items', methods=['GET'])
def items():
    tokens = load_tokens()
    metadata = load_item_metadata()
    items = []
    for item_id in tokens.keys():
        row = metadata.get(item_id, {})
        items.append(
            {
                "item_id": item_id,
                "institution_id": row.get("institution_id"),
                "institution_name": row.get("institution_name"),
            }
        )
    return jsonify({"items": items})

@app.route('/api/fetch_date_range', methods=['POST'])
def fetch_date_range():
    body = request.json or {}
    start_date_raw = body.get("start_date")
    end_date_raw = body.get("end_date")
    item_ids = normalize_str_or_list(body.get("item_id"))
    institutions = normalize_str_or_list(body.get("financial_institution"))
    account_filter = body.get("account_filter")
    include_transactions = str_to_bool(body.get("include_transactions"), default=True)
    include_balances = str_to_bool(body.get("include_balances"), default=True)

    end_date = date.today() if not end_date_raw else None
    if end_date is None:
        try:
            end_date = date.fromisoformat(end_date_raw)
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD."}), 400
    start_date = date(2000, 1, 1) if not start_date_raw else None
    if start_date is None:
        try:
            start_date = date.fromisoformat(start_date_raw)
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD."}), 400

    if start_date > end_date:
        return jsonify({"error": "start_date must be on or before end_date."}), 400
    if not include_transactions and not include_balances:
        return jsonify({"error": "At least one of include_transactions or include_balances must be true."}), 400

    tokens = load_tokens()
    if not tokens:
        return jsonify({"error": "No linked accounts found. Connect an account first."}), 400
    metadata = load_item_metadata()

    selected_item_ids = []
    if item_ids:
        unknown_item_ids = [candidate for candidate in item_ids if candidate not in tokens]
        if unknown_item_ids:
            return jsonify({"error": f"Unknown item_id(s): {unknown_item_ids}"}), 404
        selected_item_ids = item_ids
    elif institutions:
        institution_needles = [needle.lower() for needle in institutions]
        for candidate_item_id in tokens.keys():
            row = metadata.get(candidate_item_id, {})
            haystack = " ".join(
                [
                    str(row.get("institution_name", "")),
                    str(row.get("institution_id", "")),
                    candidate_item_id,
                ]
            ).lower()
            if any(needle in haystack for needle in institution_needles):
                selected_item_ids.append(candidate_item_id)
        if not selected_item_ids:
            return jsonify({"error": f"No linked items matched financial_institution={institutions}"}), 404
    else:
        selected_item_ids = list(tokens.keys())

    results = []
    for selected_item_id in selected_item_ids:
        access_token = tokens[selected_item_id]
        file = fetch_and_store(
            plaid_engine.client,
            access_token,
            item_id=selected_item_id,
            start_date=start_date,
            end_date=end_date,
            prefix="range",
            include_transactions=include_transactions,
            include_balances=include_balances,
            account_filter=account_filter,
        )
        row = metadata.get(selected_item_id, {})
        results.append(
            {
                "item_id": selected_item_id,
                "institution_id": row.get("institution_id"),
                "institution_name": row.get("institution_name"),
                "file": file,
            }
        )

    return jsonify(
        {
            "status": "Export complete",
            "filters": {
                "start_date": str(start_date),
                "end_date": str(end_date),
                "item_id": item_ids or None,
                "financial_institution": institutions or None,
                "account_filter": account_filter or None,
                "include_transactions": include_transactions,
                "include_balances": include_balances,
            },
            "results": results,
        }
    )

if __name__ == "__main__":
    app.run(port=5000)
