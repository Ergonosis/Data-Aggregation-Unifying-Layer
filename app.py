import os, json
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from extractors.plaid_ext import PlaidExtractor, fetch_and_store

load_dotenv()
app = Flask(__name__)

plaid_engine = PlaidExtractor(os.getenv("PLAID_CLIENT_ID"), os.getenv("PLAID_SECRET"), os.getenv("PLAID_ENV"))

def save_token(item_id, access_token):
    path = "storage/tokens.json"
    os.makedirs("storage", exist_ok=True)
    tokens = {}
    if os.path.exists(path):
        with open(path, 'r') as f: tokens = json.load(f)
    tokens[item_id] = access_token
    with open(path, 'w') as f: json.dump(tokens, f)

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
    save_token(exchange_resp['item_id'], access_token)
    
    # Immediate Hard Pull (Initial Data)
    file = fetch_and_store(plaid_engine.client, access_token, is_hard_pull=True)
    return jsonify({"status": "Token saved & Hard Pull complete", "file": file})

if __name__ == "__main__":
    app.run(port=5000)
