import json
import os

class FileHelper:
    DIR_WIKI = "wiki"
    os.makedirs(DIR_WIKI, exist_ok=True)

    DIR_TEMP = "temp"
    os.makedirs(DIR_TEMP, exist_ok=True)

    DIR_FILES = "files"
    os.makedirs(DIR_FILES, exist_ok=True)

    FILENAME_ITEMS_ALL = "items-all.json"
    FILENAME_ITEMS_IN_STOCK = "items-in-stock.json"
    FILENAME_NOTIFY_IN_STOCK = "notify-in-stock.json"
    FILENAME_RARITY_LEVELS = "rarity-levels.json"
    FILENAME_TYPE_RARITY_NAMES = "type-rarity-names.json"
    FILENAME_RARITIES_MD = "wiki/Home.md"

    @staticmethod
    def save_json(directory: str, filename: str, results: object):
        path_file = os.path.join(directory, filename)
        with open(path_file, "w") as writer:
            json.dump(results, writer, indent=3, sort_keys=True)


    @staticmethod
    def load_json(directory: str, filename: str) -> dict:
        path_file = os.path.join(directory, filename)
        if not os.path.exists(path_file):
            return {}

        with open(path_file, "r") as reader:
            return json.load(reader)
