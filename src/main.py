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

        self._create_inventory_page(all_items)

        in_stock = self.gag.get_items_in_stock()
        self._format_and_send_message(in_stock)


    def _create_inventory_page(self, all_items: list):
        md_lines = []
        type_rating_names = self._get_type_rarity_names(all_items)

        for item_type in sorted(type_rating_names):
            md_lines.append("<details>")
            md_lines.append(f"<summary>{item_type}</summary>")

            sort_levels = type_rating_names[item_type]
            for sort_level in sorted(sort_levels):
                md_lines.append("<details>")
                rarity = self._get_rarity_from_order_letter(sort_level)
                md_lines.append(f"<summary>{item_type} - {rarity}</summary>")

                item_names = sort_levels[sort_level]
                for item_name in item_names:
                    item = item_names[item_name]
                    description = item.get("description")
                    icon = item.get("icon")
                    last_seen = item.get("last-seen")
                    colors = item.get("colors")
                    title_html = self._create_color_table(rarity, item_name, colors)

                    md_lines.append(f"<h2>{title_html}</h2>")
                    md_lines.append("<ul>")
                    if description:
                        md_lines.append(f"<li>{description}</li>")

                    md_lines.append(f'<li><img src="{icon}" alt="{item_name}" width="200" height="200" /></li>')

                    if last_seen != self.last_seen_unknown:
                        md_lines.append(f"<li>Last Time Available: {last_seen}</li>")

                    md_lines.append("</ul>")

                md_lines.append("</details>")

            md_lines.append("</details>")
            md_lines.append("<hr />")

        md_str = os.linesep.join(md_lines)
        with open(FileHelper.FILENAME_RARITIES_MD, "w") as writer:
            writer.write(md_str)


    def _create_color_table(self, rarity: str, item_name: str, colors: list) -> str:
        if not colors:
            return ""

        total_width = 150
        total_colors = len(colors)
        color_width = round(total_width / total_colors, 1)

        table_lines = []
        table_lines.append("<table>")

        table_lines.append("<tr>")
        table_lines.extend(self._create_color_tds(colors, color_width))
        table_lines.append("</tr>")

        table_lines.append("<tr>")
        table_lines.append(f'<td colspan="{total_colors}">{rarity} - {item_name}</td>')
        table_lines.append("<tr>")

        table_lines.append("<tr>")
        table_lines.extend(self._create_color_tds(colors, color_width))
        table_lines.append("</tr>")

        return "".join(table_lines)


    def _create_color_tds(self, colors: list, color_width: str) -> list:
        td_list = []
        for color in colors:
            td_list.append(f'<td style="background-color: {color}; width: {color_width}px;"></td>')

        return td_list



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

        for order_letter in self.rarity_levels:
            item = self.rarity_levels[order_letter]
            item_name = item.get("name")
            if rarity.lower() == item_name.lower():
                return item.get("color")


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
