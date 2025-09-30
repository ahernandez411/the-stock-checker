import json
import os

from lib.file_helper import FileHelper

class Sandbox:
    def run(self):
        path_items_all = "temp\items-all.json"
        items_all = []
        with open(path_items_all, "r") as reader:
            items_all = json.load(reader)

        simplified = {}
        for item in items_all:
            type = item.get("type")
            if type != "seed":
                continue

            name = item.get("display_name")
            rarity = item.get("rarity")

            simplified[name] = rarity

        FileHelper.save_json("all-seeds.json", simplified)



if __name__ == "__main__":
    Sandbox().run()
