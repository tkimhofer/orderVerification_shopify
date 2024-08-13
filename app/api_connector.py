# import asyncio
import base64
import datetime as dt
from flask import request, abort
import hashlib
import hmac
import os

from app.messaging_service import TelegramBot
from app.quality_assurance_toolbox import OrderCheckShopify

# ideas/thoughts regarding extensions
# use logging library for app monitoring / health checks
# submit heavy-workload processes as background job (eg. managing payload computations)
# ORM framework might simplify if direct interaction with SQL DB desired

from functools import wraps
import time


def print_runtime(func):
    @wraps(func)
    def _runtime(*args, **kwargs):
        t1 = time.time()
        out = func(*args, **kwargs)
        t2 = time.perf_counter()
        runtime = t2 - t1
        print(f'Runtime {func.__name__}{args}: {runtime:.6f} s')
        return out
    return print_runtime


class ShopifyWebhookHandler:
    def __init__(self,):
        # load webhook auth secret
        self.secret = os.environ.get("secret")

        # define recipients and instantiate messenger
        self.stakeholders = {'7314801516': 'karen from finance'} # format: {str(chat_id): name}
        self.admin = {'xxx': 'admin'}
        self.Messenger = TelegramBot()

    def authenticate_hmac(self, auth_header = 'X-Shopify-Hmac-Sha256'):
        '''authenticate webhook using hmac'''

        hdig = hmac.new(
            self.secret.encode('utf-8'),
            request.get_data(),
            hashlib.sha256
        ).digest()
        hdig_b64 = base64.b64encode(hdig).decode()

        return hmac.compare_digest(hdig_b64, request.headers.get(auth_header))

    def handle_order_paid(self):
        """authorise and run quality monitoring workflow, send resp. http responsem code"""

        # verify origin
        if not self.authenticate_hmac():
            abort(403)

        # run quality monitor pipline
        self.process_payload_lineitems()
        return 'Webhook received', 200

    # @print_runtime
    def process_payload_lineitems(self):
        '''run order-quality monitoring workflow'''
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


