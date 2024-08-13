import datetime as dt
import os
import requests


class TelegramBot:
    service = 'telegram'

    def __init__(self):
        self.url = os.path.join(os.environ.get("url"), 'sendMessage') # telegram api
        self.token = os.environ.get("token") # api secret

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
                # print(f"""\t{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Bot failed messaging "{name}" with status {r.status_code}""")
                raise ValueError(f"""{dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Bot failed messaging to "{name}" with status {r.status_code}: {str(dt.datetime.now())}""")


# contacts = {
#     '7314801516': 'karen from finance'
# }
# messenger = TelegramBot(contacts)
# messenger.send_message('hi karen!', contacts)