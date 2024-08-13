from flask import Flask
from dotenv import load_dotenv

# Note: set-up for testin (not production)

load_dotenv('.env', override=True)
from app.api_connector import ShopifyWebhookHandler

app = Flask(__name__)

# instantiate wh-handler and define endpoint for newly paid orders
shopify_qc =  ShopifyWebhookHandler()

@app.route('/orders/paid', methods=['POST'])
def webhook():
    return shopify_qc.handle_order_paid()

# obtain static IP addr and configure firewall for traffic on resp. port
# run application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9011,)

# recommendations/suggestions for production mode:
# obtain static IP addr (on cloud: configure firewall for traffic on resp. port)
# run with gunicorn/wsgi - gage nb workers with cores available / expected rate of webhooks events
# set up reverse proxy to handle incoming traffic and balance workload (eg, with nginx)
# thoroughly test workflow using different scenarios
