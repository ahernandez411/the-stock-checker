import json
import os

class FileHelper:
    DIR_TEMP = "temp"
    os.makedirs(DIR_TEMP, exist_ok=True)


    @staticmethod
    def save_json(filename: str, results: object):
        path_file = os.path.join(FileHelper.DIR_TEMP, filename)
        with open(path_file, "w") as writer:
            json.dump(results, writer, indent=3, sort_keys=True)