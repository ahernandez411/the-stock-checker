import os

class EnvReader:
    def __init__(self):
        self.ntfy_name = os.getenv("NTFY_NAME")
        self.api_key = os.getenv("JSTUDIO_API_KEY")
        self.secret_key = os.getenv("JSTUDIO_SECRET_KEY")
