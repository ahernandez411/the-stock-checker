import os

from lib.env_reader import EnvReader
from lib.file_helper import FileHelper
from lib.gag_reader import GAGReader
from lib.ntfy_handler import NtfyHandler

class Main:
    def __init__(self):
        envs = EnvReader()
        notify_in_stock = FileHelper.load_json(FileHelper.DIR_FILES, "notify-in-stock.json")
        self.gag = GAGReader(envs, notify_in_stock)
        self.ntfy = NtfyHandler(envs)
        self.notify_in_stock = notify_in_stock


    def run(self):
        print("----------------------------------------")
        print("Check Stocks")
        print("----------------------------------------")

        self._show_watched_items()

        in_stock = self.gag.get_items_in_stock()
        self._format_and_send_message(in_stock)


    def _format_and_send_message(self, in_stock: dict):
        if not in_stock:
            print("There are zero watched items in stock")

        else:
            message_lines = []
            for stock_category in in_stock:
                message_lines.append(stock_category)

                item = in_stock[stock_category]

                message_lines.append(f"- Name: {item['name']}")
                message_lines.append(f"- Quantity: {item['quantity']}")
                message_lines.append(f"- Leaves at: {item['end-time']}")

            message_str = os.linesep.join(message_lines)
            self.ntfy.send_message("In Stock Items", message_str)


    def _show_watched_items(self):
        print("Looking for the following items:")
        for stock_category in self.notify_in_stock:
            print("")
            print(stock_category)
            for item in self.notify_in_stock[stock_category]:
                print(f"- {item}")


if __name__ == "__main__":
    app = Main()
    app.run()
