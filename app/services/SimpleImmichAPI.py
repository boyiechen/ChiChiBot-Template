# app/services/ImmichAPI.py

import os
import sys
import requests
import json
import pandas as pd
from icecream import ic
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import IMMICH_API_BASE_URL, IMMICH_API_TOKEN


class ImmichAPI:

    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.headers = {
            'Accept': 'application/json',
            'x-api-key': access_token
        }
    
    def get_albums(self):
        url = f"{self.base_url}/api/album"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def convert_json_album_todataframe(self, json_album):
        df = pd.DataFrame(json_album)
        return df
    
    def getAllUsers(self):
        url = f"{self.base_url}/api/user?isAll=true"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def getAllSharedLinks(self):
        url = f"{self.base_url}/api/shared-link"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    # test ImmichAPI
    
    immich_client = ImmichAPI(IMMICH_API_BASE_URL, IMMICH_API_TOKEN)
    albums = immich_client.get_albums()
    albums = immich_client.convert_json_album_todataframe(albums)
    ic(albums.head())
    albums.to_csv("./tmp/albums.csv", index=False)
    print(albums.columns)

    users = immich_client.getAllUsers()
    users = pd.DataFrame(users)
    ic(users)

    shared_links = immich_client.getAllSharedLinks()
    ic(shared_links)
    shared_links = pd.DataFrame(shared_links)
    ic(shared_links)
    shared_links.to_csv("./tmp/shared_links.csv", index=False)
