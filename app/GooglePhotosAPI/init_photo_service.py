import os
from Google import Create_Service

API_NAME = 'photoslibrary'
API_VERSION = 'v1'
# CLIENT_SECRET_FILE = './app/credentials/gphoto_client_secret.json'
CLIENT_SECRET_FILE = './app/credentials/client_secret_family.json'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.sharing',
          'https://www.googleapis.com/auth/photoslibrary',
          'https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata']

service = Create_Service(CLIENT_SECRET_FILE,API_NAME, API_VERSION, SCOPES)
print(dir(service))