import hmac
import hashlib
import base64
import numpy as np

import pandas as pd
import requests
import json

class ShopifyWebhookSimulator:
    def __init__(self,):
        self.shared_secret = 'torben'

    def generate_hmac(self, data):
        """
        Generate an HMAC SHA256 signature for the given data.
        """
        digest = hmac.new(
            self.shared_secret.encode('utf-8'),
            data,
            hashlib.sha256
        ).digest()

        return base64.b64encode(digest).decode()

    def send_webhook(self, url, payload):
        """
        Send a simulated Shopify webhook to the specified URL.
        """
        # Convert the payload to JSON
        json_data = json.dumps(payload)

        # Generate the HMAC header
        hmac_header = self.generate_hmac(json_data.encode('utf-8'))

        # Set the headers including the HMAC signature
        headers = {
            'Content-Type': 'application/json',
            'X-Shopify-Hmac-Sha256': hmac_header
        }

        # Send the POST request to the webhook URL
        response = requests.post(url, headers=headers, data=json_data)

        # Print the response status code and text
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

# Your Shopify shared secret (the same secret used in your webhook verification)

print('creating simulator')
# Create an instance of the simulator
simulator = ShopifyWebhookSimulator()

# Define the webhook endpoint you want to send the simulated webhook to
webhook_url = 'http://192.168.178.29:9011/orders/paid'  # Replace with your actual webhook endpoint
print(webhook_url)
# Define the payload that mimics a Shopify webhook

# Define the bundles
starterSet4w = {
        'type': 'static price combo',
        'components': {
            'sku-001': {'n': 4, 'variant_sku': None, 'pricing': True}, # 4 packs of diet-powder
            'sku-002': {'n': 1, 'variant_sku': None, 'pricing': False},  # free shaker
            'sku-003': {'n': 1, 'variant_sku': None, 'pricing': False},  # free diet plan
            'sku-004': {'n': 1, 'variant_sku': None, 'pricing': False},  # free cookbook
            'sku-005': {'n': 1, 'variant_sku': None, 'pricing': False},  # free vitamins
        }
}

# buy one-get one (10% discount on specific flavour variant)
bogo10 = {
        'type': 'BOGO 10%',
        'components': {
            'sku-001': {'n': 1, 'variant_sku': None, 'pricing': True},
            'sku-002': {'n': 1, 'variant_sku': 'sku-001-099', 'pricing': 'd10'},  # 10% discount for new flavour variant
        }
}

# define combined bundle
nested_bundle = {
    'sku-300': {  # Parent bundle: StarterSet 4w + BOGO
        'type': 'nested bundle',
        'components': {
            # child bundles
            'sku-100': starterSet4w,
            'sku-200': bogo10
        }
    }
}


## Test order #4
# 1 x nested_bundle where bogo variant is free instead of discounted + 1 bogo flavour variant full paid
order_id = 4
items_sold = [1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1] # item quantity
n_prod =  len(items_sold) # product defined here as sellable unit that may or may not be available in different variants

order_4 = {
    'order_line_item_id': [f'oli-{i}' for i in range(1,n_prod+1)],
    'order_line_id': list(range(1, n_prod+1)),
    'order_id': [f'#{order_id}'] * n_prod,

    'product_id':
        ['mf-b-4wStarterSet'] +
        ['mf-p-powder'] * 3 +
        ['mf-p-shaker', 'mf-p-dplan', 'mf-p-cookbook', 'mf-p-vitamins'] +
        ['mf-p-powder', 'mf-p-powder', 'mf-p-powder'],
    'product_price': [None] + [179.84 / 4] * 2 + [179.84 / 4 * 2] + [0.] * 4 + [179.84 / 4, 0, 179.84 / 4] ,  # Price in purchase order

    'item_index': np.cumsum(items_sold).tolist(),
    'items_sold': items_sold,
    'item_sku': [ # format sku-[a]-[b] -> sku-[a] is the product_sku
        'sku-300-001',
        'sku-001-001', 'sku-001-002', 'sku-001-003',
        'sku-002-001', 'sku-003-001', 'sku-004-001', 'sku-005-001',
        'sku-001-004', 'sku-001-099', 'sku-001-099'
    ],

    'bundle_id': ['sku-200-StarterSet4w'] * n_prod,
    'bundle_property': [json.dumps(nested_bundle)] * (n_prod-1) + [None],
}

order_4['product_sku'] =  [x[:7] for x in order_4['item_sku']]
order_4['product_price'][0] = sum(order_4['product_price'][1:])


payload = order_4
df = pd.DataFrame(payload)

print('sending webhook')
# Send the simulated webhook
simulator.send_webhook(webhook_url, payload)
print('done')