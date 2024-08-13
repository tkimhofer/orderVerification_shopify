from dotenv import load_dotenv
import datetime as dt
import os
import requests


class TelegramBot:
    service = 'telegram'

    def __init__(self):

        self.url = os.path.join(os.environ.get("url"), 'sendMessage')
        self.token = os.environ.get("token")

    def log_message(self):

        if self.free_item_mismatch['excess'] or self.free_item_mismatch['lack']:

            message = f'***Quality Issue in Order {self.order_id}***\n\n'

            skus = '-' if not self.free_item_mismatch['excess'] else "\n".join(
                f"{sku[0]} (n={n})" for sku, n in self.free_item_mismatch['excess'].items())
            message += "Unaccounted free item(s): " + skus + '\n\n'

            skus = '-' if not self.free_item_mismatch['lack'] else "\n".join(
                f"{sku[0]} (n={n})" for sku, n in self.free_item_mismatch['lack'].items())
            message += "Missing free item(s): " + skus + '\n\n'

            message += f'Manual review of Order {self.order_id} advised \U0001F60A'
            return True, message

        else:
            # not messaging stakeholders
            # todo: log result (e.g. append order_id to text file)
            return False, f'No Issue Detected in Order {self.order_id}\n'

    def send_message(self, message: str, recipients: dict):
        payload = {'text': message}
        responses = []
        for id, name in recipients.items():
            payload['chat_id'] = id
            r = requests.post(self.url, data=payload)
            responses.append(r)
            if r.status_code == 200:
                print(f"""\t-> Message sent to "{name}" """)
            else:
                print(f"""\t{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Bot failed messaging "{name}" with status {r.status_code}""")
                # document and notify admin
                raise ValueError(f"""!Bot failed messaging to "{name}" with status {r.status_code}: {str(dt.datetime.now())}""")


# contacts = {
#     '7314801516': 'karen from finance'
# }
# bot = Messenger(contacts)
# bot.send_message('hi there')