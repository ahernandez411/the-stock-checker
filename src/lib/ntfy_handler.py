import json
import requests

from lib.env_reader import EnvReader

class NtfyHandler:
    # https://docs.ntfy.sh/publish/
    def __init__(self, envs: EnvReader):
        ntfy_name = envs.ntfy_name
        self.api_url = f"https://ntfy.sh/{ntfy_name}"


    def send_message(self, header: str, message: str):
        print(f"Sending notification to {self.api_url}")

        if not isinstance(message, str):
            message = json.dumps(message)

        encoded = message
        headers = {
            "Title": header,
            "Priority": "default"
        }

        response = requests.post(self.api_url, data=encoded, headers=headers)
        results = response.json()
        print(results)
