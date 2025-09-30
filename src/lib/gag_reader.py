import requests

from datetime import datetime
from lib.env_reader import EnvReader
from lib.file_helper import FileHelper

class GAGReader:
    # https://api.joshlei.com/
    def __init__(self, envs: EnvReader, notify_in_stock: dict):
        self.envs = envs

        self.notify_egg_stock = notify_in_stock.get("egg_stock", [])
        self.notify_gear_stock = notify_in_stock.get("gear_stock", [])
        self.notify_seed_stock = notify_in_stock.get("seed_stock", [])

        self.headers = {
            "accept": "application/json",
            "jstudio-key": self.envs.api_key
        }

        self.base_api = "https://api.joshlei.com/v2/growagarden"


    def get_items_in_stock(self) -> dict:
        print("")
        print("Check if items are in stock")

        api_url = f"{self.base_api}/stock"
        response = requests.get(api_url, headers=self.headers)
        results = response.json()

        FileHelper.save_json(FileHelper.DIR_TEMP, "items-in-stock.json", results)

        in_stock_items = {}
        if self.notify_egg_stock:
            self._add_if_in_stock(in_stock_items, results, "egg_stock", self.notify_egg_stock)

        if self.notify_gear_stock:
            self._add_if_in_stock(in_stock_items, results, "gear_stock", self.notify_gear_stock)

        if self.notify_seed_stock:
            self._add_if_in_stock(in_stock_items, results, "seed_stock", self.notify_seed_stock)

        if not in_stock_items:
            print("Zero watched items in stock!")

        return in_stock_items


    def get_items_all(self) -> dict:
        api_url = f"{self.base_api}/info?type=seed"
        response = requests.get(api_url, headers=self.headers)
        results = response.json()

        FileHelper.save_json(FileHelper.DIR_TEMP, "items-all.json", results)

        return results


    def _add_if_in_stock(self, in_stock_items: dict, current_stock: dict, stock_category: str, notify_stocks: list):
        print(f"Look in {stock_category}")

        current_egg_stock = current_stock[stock_category]
        for current in current_egg_stock:
            name = current.get("display_name")

            if name.lower() in notify_stocks:
                print(f"{name} is in stock!")
                if stock_category not in in_stock_items:
                    in_stock_items[stock_category] = {}

                quantity = current.get("quantity")
                end_time = current.get("Date_End")

                in_stock_items[stock_category][name] = {
                    "name": name,
                    "quantity": quantity,
                    "end-time": end_time,
                }


    def _convert_date_str_to_friendly_time(self, date_str: str) -> str:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.000Z")
        formatted = dt.strftime("%Y-%m-%d %I:%M %p")
        return formatted
