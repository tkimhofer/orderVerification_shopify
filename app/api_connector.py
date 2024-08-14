# import asyncio
import base64
import datetime as dt
from flask import request, abort
import hashlib
import hmac
import os

from app.messaging_service import TelegramBot
from app.quality_assurance_toolbox import OrderCheckShopify

class ShopifyWebhookHandler:
    def __init__(self,):
        # load parameters / secret
        self.secret = os.environ.get("secret")

        # define recipients and instantiate messenger
        self.stakeholders = {'7314801516': 'karen from finance'} # format: {str(chat_id): name}
        self.admin = {'xxx': 'admin'}
        self.Messenger = TelegramBot()

    def authenticate_hmac(self, auth_header = 'X-Shopify-Hmac-Sha256'):
        '''authenticate request using hmac
            Args:
                auth_header (str): http request auth header
            Returns:
                bool: True if verification succeeded
        '''

        hdig = hmac.new(
            self.secret.encode('utf-8'),
            request.get_data(),
            hashlib.sha256
        ).digest()
        hdig_b64 = base64.b64encode(hdig).decode()

        return hmac.compare_digest(hdig_b64, request.headers.get(auth_header))

    def handle_order_paid(self):
        """authorise and run workflow for payload, send resp. response code"""

        # verify origin
        if not self.authenticate_hmac():
            abort(403)

        # run quality monitor pipline
        self.process_payload_lineitems()
        return 'Webhook received', 200

    # @print_runtime
    def process_payload_lineitems(self):
        '''run order quality check workflow, if it errors -> notify admin'''
        try:
            # instantiate order obj, run workflow & create notification message
            Order = OrderCheckShopify(request.json)
            Order.validate_basket_items()
            message = Order.create_message()

            if message[0]: # is true if item mismatches are found
                print(f'{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Quality issues found for order {Order.order_id}')
                self.Messenger.send_message(message[1], recipients=self.stakeholders)
            else:
                print(f'{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: No quality issues found for order {Order.order_id}.')
        except:
            print(f'{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Order monitor pipeline failed!')
            message = (True, f'Admin - order monitor pipline failed for\n{request.json}')
            self.Messenger.send_message(message[1], recipients=self.admin)



# ideas/thoughts regarding extensions
# use logging library for app monitoring / health checks
# submit heavy-workload processes as background job (eg. managing payload computations)
# ORM framework might simplify if direct interaction with SQL DB desired
