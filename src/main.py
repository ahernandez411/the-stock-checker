import os

from lib.env_reader import EnvReader
from lib.gag_reader import GAGReader
from lib.ntfy_handler import NtfyHandler

class Main:
    def __init__(self):
        envs = EnvReader()
        self.gag = GAGReader(envs)
        self.ntfy = NtfyHandler(envs)

    def run(self):
        in_stock = self.gag.get_items_in_stock()
        print(in_stock)

        all = self.gag.get_items_all()
        print(all)
        
        self.ntfy.send_message("From Adam", in_stock.get("seed_stock"))


if __name__ == "__main__":
    app = Main()
    app.run()