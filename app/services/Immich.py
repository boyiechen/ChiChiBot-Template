# ImmichAPI.py

import requests
import logging
import datetime
import os
import sys
from icecream import ic


# Set up logger to log in logfmt format
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='time=%(asctime)s level=%(levelname)s msg=%(message)s')
logging.Formatter.formatTime = (lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc).astimezone().isoformat(sep="T",timespec="milliseconds"))

def initialize(api_url, api_key):
    global root_url, requests_kwargs, version

    root_url = api_url
    if root_url[-1] != '/':
        root_url = root_url + '/'

    requests_kwargs = {
        'headers' : {
            'x-api-key': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    }

    version = fetchServerVersion()

def fetchServerVersion():
    version = {'major': 1, 'minor': 105, "patch": 1}
    r = requests.get(root_url+'server-info/version', **requests_kwargs)
    if r.status_code == 200:
        ic(r)
        version = r.json()
        logging.info("Detected Immich server version %s.%s.%s", version['major'], version['minor'], version['patch'])
    else:
        logging.info("Detected Immich server version %s.%s.%s or older", version['major'], version['minor'], version['patch'])
    return version

def fetchAssets():
    if version['major'] == 1 and version['minor'] <= 105:
        return fetchAssetsLegacy()
    else:
        return fetchAssetsMinorV106()

def fetchAssetsLegacy():
    assets = []
    r = requests.get(root_url+'asset?take=5000', **requests_kwargs)
    if r.status_code == 200:
        assets = r.json()
    return assets

def fetchAssetsMinorV106():
    assets = []
    body = {'isNotInAlbum': 'true', 'size': 1000, 'page': 1}
    r = requests.post(root_url+'search/metadata', json=body, **requests_kwargs)
    if r.status_code == 200:
        responseJson = r.json()
        assets = responseJson['assets']['items']
    return assets

def fetchAlbums():
    apiEndpoint = 'albums' if version['major'] > 1 or version['minor'] > 105 else 'album'
    r = requests.get(root_url+apiEndpoint, **requests_kwargs)
    if r.status_code == 200:
        return r.json()
    return []

def createAlbum(albumName):
    apiEndpoint = 'albums' if version['major'] > 1 or version['minor'] > 105 else 'album'
    data = {'albumName': albumName, 'description': albumName, 'hasSharedLink': True}
    r = requests.post(root_url+apiEndpoint, json=data, **requests_kwargs)
    if r.status_code in [200, 201]:
        return r.json()['id']
    return None

def addAssetsToAlbum(albumId, assets):
    apiEndpoint = 'albums' if version['major'] > 1 or version['minor'] > 105 else 'album'
    assets_chunked = list(divide_chunks(assets, 2000))
    for assets_chunk in assets_chunked:
        data = {'ids': assets_chunk}
        r = requests.put(root_url+apiEndpoint+f'/{albumId}/assets', json=data, **requests_kwargs)
        if r.status_code not in [200, 201]:
            continue

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def upload_file(file_path, device_asset_id, device_id, created_at, modified_at, is_favorite=False, key=None, duration=None, is_archived=False, is_external=False, is_offline=False, is_read_only=False, is_visible=True, library_id=None, live_photo_data=None, sidecar_data=None):
    with open(file_path, 'rb') as f:
        files = {'assetData': f}
        data = {
            'deviceAssetId': device_asset_id,
            'deviceId': device_id,
            'fileCreatedAt': created_at,
            'fileModifiedAt': modified_at,
            'isFavorite': str(is_favorite).lower(),
            'key': key,
            'duration': duration,
            'isArchived': str(is_archived).lower(),
            'isExternal': str(is_external).lower(),
            'isOffline': str(is_offline).lower(),
            'isReadOnly': str(is_read_only).lower(),
            'isVisible': str(is_visible).lower(),
            'libraryId': library_id,
            'livePhotoData': live_photo_data,
            'sidecarData': sidecar_data
        }
        r = requests.post(root_url+'asset/upload', files=files, data=data, headers={'x-api-key': requests_kwargs['headers']['x-api-key']})
        if r.status_code in [200, 201]:
            return r.json()['id']
    return None

def add_user_to_album(album_id, user_id, role="editor"):
    apiEndpoint = f'album/{album_id}/users'
    data = {
        "albumUsers": [
            {
                "role": role,
                "userId": user_id
            }
        ]
    }
    r = requests.put(root_url+apiEndpoint, json=data, **requests_kwargs)
    if r.status_code in [200, 201]:
        return True
    return False

def create_shared_link(album_id, asset_ids, allow_download=True, allow_upload=True, show_metadata=True, description=None, expires_at=None, password=None):
    apiEndpoint = 'shared-link'
    data = {
        "albumId": album_id,
        "allowDownload": allow_download,
        "allowUpload": allow_upload,
        "assetIds": asset_ids,
        "showMetadata": show_metadata,
        "description": description,
        "expiresAt": expires_at,
        "password": password,
        "type": "ALBUM",
        "hasSharedLink": True,
    }
    r = requests.post(root_url+apiEndpoint, json=data, **requests_kwargs)
    # ic(r.text)
    res = r.json()
    # ic(res)
    shared_album_id = res.get('id')

    res_links = getSharedLinkByID(shared_album_id)
    # ic(res_links)
    return res_links

def getSharedLinkByID(id):
    apiEndpoint = f'shared-link/{id}'
    r = requests.get(root_url+apiEndpoint, **requests_kwargs)
    if r.status_code in [200, 201]:
        res = r.json()
        ic(res)
        return res
    return None
