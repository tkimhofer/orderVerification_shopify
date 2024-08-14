# Note: app set-up for testing (not production)
from flask import Flask
from dotenv import load_dotenv
load_dotenv('.env', override=True)
from app.api_connector import ShopifyWebhookHandler

app = Flask(__name__)

# instantiate and ShopifyWebhookHandler
shopify_qc =  ShopifyWebhookHandler()

# define endpoint
@app.route('/orders/paid', methods=['POST'])
def webhook():
    return shopify_qc.handle_order_paid()

# run application / adjust port
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000,)

# recommendations/suggestions for production mode:
# obtain static IP addr (on cloud: configure firewall for traffic on resp. port)
# run with gunicorn/wsgi - gage nb workers with cores available / expected rate of webhooks events
# set up reverse proxy to handle incoming traffic and balance workload (eg, with nginx)
# thoroughly test workflow using different scenarios
