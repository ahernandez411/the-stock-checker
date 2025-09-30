import requests

from lib.env_reader import EnvReader
from lib.file_helper import FileHelper

class GAGReader:
    # https://api.joshlei.com/
    def __init__(self, envs: EnvReader):
        self.envs = envs

        self.headers = {
            "accept": "application/json",
            "jstudio-key": self.envs.api_key
        }
        self.base_api = "https://api.joshlei.com/v2/growagarden"


    def get_items_in_stock(self) -> dict:
        api_url = f"{self.base_api}/stock"
        response = requests.get(api_url, headers=self.headers)
        results = response.json()            
                    
        FileHelper.save_json("items-in-stock.json", results)

        return results
    

    def get_items_all(self) -> dict:
        api_url = f"{self.base_api}/info?type=seed"
        response = requests.get(api_url, headers=self.headers)
        results = response.json()

        FileHelper.save_json("items-all.json", results)

        return results
        

    
