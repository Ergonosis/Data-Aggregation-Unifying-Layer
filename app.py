import os, json
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
from extractors.plaid_ext import PlaidExtractor

load_dotenv()
app = Flask(__name__)

# Ensure Storage Folder Exists
os.makedirs("storage", exist_ok=True)

# Initialize Plaid
plaid_engine = PlaidExtractor(
    os.getenv("PLAID_CLIENT_ID"), 
    os.getenv("PLAID_SECRET"), 
    os.getenv("PLAID_ENV")
)

@app.route('/')
def index():
    with open('index.html', 'r') as f:
        return render_template_string(f.read())

@app.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    """Step 1: Create a link_token for the frontend."""
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.products import Products
    from plaid.model.country_code import CountryCode

    request_data = LinkTokenCreateRequest(
        products=[Products('transactions')],
        client_name="Data Aggregation Service",
        country_codes=[CountryCode('US')],
        language='en',
        user=LinkTokenCreateRequestUser(client_user_id='unique_user_id_123')
    )
    response = plaid_engine.client.link_token_create(request_data)
    return jsonify(response.to_dict())

@app.route('/api/exchange_public_token', methods=['POST'])
def exchange_token():
    """Step 3: Exchange public_token for permanent access_token."""
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
    
    public_token = request.json.get('public_token')
    exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
    exchange_response = plaid_engine.client.item_public_token_exchange(exchange_request)
    
    # Securely identifying the item
    access_token = exchange_response['access_token']
    
    # Step 4: Use access_token to fetch and store data
    data = plaid_engine.get_transactions(access_token)
    
    # Persistence Layer: Store as JSON
    filename = f"storage/transactions_{exchange_response['item_id']}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=4, default=str)
        
    return jsonify({"status": "complete", "file_saved": filename})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
