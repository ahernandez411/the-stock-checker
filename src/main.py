import os
import pytz

from datetime import datetime, timezone
from lib.env_reader import EnvReader
from lib.file_helper import FileHelper
from lib.gag_reader import GAGReader
from lib.ntfy_handler import NtfyHandler

class Main:
    def __init__(self):
        envs = EnvReader()
        notify_in_stock = FileHelper.load_json(FileHelper.DIR_FILES, FileHelper.FILENAME_NOTIFY_IN_STOCK)
        self.rarity_levels = FileHelper.load_json(FileHelper.DIR_FILES, FileHelper.FILENAME_RARITY_LEVELS)
        self.gag = GAGReader(envs, notify_in_stock)
        self.ntfy = NtfyHandler(envs)
        self.rarity_none = "I"
        self.last_seen_unknown = "Unknown"


    def run(self):
        print("----------------------------------------")
        print("Check Stocks")
        print("----------------------------------------")

        all_items = FileHelper.load_json(FileHelper.DIR_TEMP, FileHelper.FILENAME_ITEMS_ALL)
        if not all_items:
            all_items = self.gag.get_items_all()

        self._create_wiki_pages(all_items)

        in_stock = self.gag.get_items_in_stock()
        self._format_and_send_message(in_stock)


    def _create_wiki_pages(self, all_items: list):
        home_md_list = [
            "# Item Categories",
            "",
        ]

        type_rating_names = self._get_type_rarity_names(all_items)
        for item_type in sorted(type_rating_names):
            home_md_list.append(f"- [{item_type}]({item_type})")

            category_md_list = [
                f"# {item_type}",
                ""
            ]

            sort_levels = type_rating_names[item_type]
            for sort_level in sorted(sort_levels):
                rarity = self._get_rarity_from_order_letter(sort_level)

                colors = "".join(self._get_rarity_colors(rarity))

                category_md_list.append("")
                category_md_list.append("")
                category_md_list.append(colors)
                category_md_list.append("")
                category_md_list.append(rarity)
                category_md_list.append("")
                category_md_list.append(colors)
                category_md_list.append("")

                item_names = [f"`{item}`" for item in sort_levels[sort_level]]

                names_csv = ", ".join(item_names)
                category_md_list.append(f"- {names_csv}")

            path_wiki_category = os.path.join(FileHelper.DIR_WIKI, f"{item_type}.md")
            category_md = os.linesep.join(category_md_list)
            with open(path_wiki_category, "w") as writer:
                writer.write(category_md)

        home_md = os.linesep.join(home_md_list)
        path_wiki_home = os.path.join(FileHelper.DIR_WIKI, "Home.md")
        with open(path_wiki_home, "w") as writer:
            writer.write(home_md)


    def _get_type_rarity_names(self, all_items) -> dict:
        type_rarity_names = {}
        for item in all_items:
            item_type = item.get("type").title()
            item_rarity = item.get("rarity")
            rating_sort = self._get_rarity_order_letter(item_rarity)
            item_name = item.get("display_name")
            item_description = item.get("description")
            item_icon = item.get("icon")
            item_last_seen = self._get_last_seen(item.get("last_seen"))
            item_colors = self._get_rarity_colors(item_rarity)

            if item_type not in type_rarity_names:
                type_rarity_names[item_type] = {}

            if rating_sort not in type_rarity_names[item_type]:
                type_rarity_names[item_type][rating_sort] = {}

            if item_name not in type_rarity_names[item_type][rating_sort]:
                type_rarity_names[item_type][rating_sort][item_name] = {
                    "description": item_description,
                    "icon": item_icon,
                    "last-seen": item_last_seen,
                    "rarity": item_rarity,
                    "colors": item_colors,
                }

        FileHelper.save_json(FileHelper.DIR_TEMP, FileHelper.FILENAME_TYPE_RARITY_NAMES, type_rarity_names)
        return type_rarity_names


    def _get_last_seen(self, timestamp_str: str) -> str:
        if timestamp_str == "0":
            return self.last_seen_unknown

        timestamp = int(timestamp_str)
        tz_denver = pytz.timezone("America/Denver")
        utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        mountain_time = utc_time.astimezone(tz_denver)

        last_seen = mountain_time.strftime("%A %B %-d, %Y at %I:%M %p")
        return last_seen


    def _get_rarity_order_letter(self, rarity: str) -> str:
        if not rarity:
            return self.rarity_none

        for order_letter in self.rarity_levels:
            item = self.rarity_levels[order_letter]
            item_name = item.get("name")
            if rarity.lower() == item_name.lower():
                return order_letter

        return self.rarity_none


    def _get_rarity_from_order_letter(self, order_letter: str) -> str:
        item = self.rarity_levels.get(order_letter)
        if not item:
            item = self.rarity_levels.get(self.rarity_none)

        item_rarity = item.get("name")
        return item_rarity



    def _get_rarity_colors(self, rarity: str) -> list:
        if not rarity:
            return self.rarity_levels[self.rarity_none].get("color")

        colors = []
        for order_letter in self.rarity_levels:
            item = self.rarity_levels[order_letter]
            item_name = item.get("name")
            if rarity.lower() == item_name.lower():
                colors = item.get("color")

        if len(colors) == 1:
            dupes = []
            color = colors[0]
            for _ in range(6):
                dupes.append(color)

            colors = dupes

        return colors


    def _format_and_send_message(self, in_stock: dict):
        if not in_stock:
            print(" ")
            print("There are zero watched items in stock")

        else:
            message_lines = []
            for stock_category in in_stock:
                message_lines.append(stock_category)

                items = in_stock[stock_category]
                for item in items:
                    message_lines.append("-------------------------------")
                    message_lines.append(f"Name: {item['name']}")
                    message_lines.append("-------------------------------")
                    message_lines.append(f"- Quantity: {item['quantity']}")
                    message_lines.append(f"- In Stock from {item['end-time']} to {item['start-time']}")

            message_str = os.linesep.join(message_lines)
            self.ntfy.send_message("In Stock Items", message_str)



if __name__ == "__main__":
    app = Main()
    app.run()
