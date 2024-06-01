"""
batchCretae method
"""
import os
import pickle
import requests

# step 1: Upload byte data to Google Server
image_dir = os.path.join(os.getcwd(), 'app/img_upload')
upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
token = pickle.load(open('token_photoslibrary_v1.pickle', 'rb'))
from init_photo_service import service

headers = {
    'Authorization': 'Bearer ' + token.token,
    'Content-type': 'application/octet-stream',
    'X-Goog-Upload-Protocol': 'raw'
}

image_file = os.path.join(image_dir, 'test.jpg')
headers['X-Goog-Upload-File-Name'] = 'LlAMA.jpg'

img = open(image_file, 'rb').read()
response = requests.post(upload_url, data=img, headers=headers)

request_body  = {
    'newMediaItems': [
        {
            'description': 'Kuma the corgi',
            'simpleMediaItem': {
                'uploadToken': response.content.decode('utf-8')
            }
        }
    ]
}

upload_response = service.mediaItems().batchCreate(body=request_body).execute()


def upload_image(image_path, upload_file_name, token):
    headers = {
        'Authorization': 'Bearer ' + token.token,
        'Content-type': 'application/octet-stream',
        'X-Goog-Upload-Protocol': 'raw',
        'X-Goog-File-Name': upload_file_name
    }    

    img = open(image_path, 'rb').read()
    response = requests.post(upload_url, data=img, headers=headers)
    print('\nUpload token: {0}'.format(response.content.decode('utf-8')))
    return response


tokens = []
image_dir = os.path.join(os.getcwd(), 'app/img_upload')
upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
token = pickle.load(open('token_photoslibrary_v1.pickle', 'rb'))

image_skytower = os.path.join(image_dir, 'screenshot.png')
response = upload_image(image_skytower, 'Tokyo Skytower', token)
tokens.append(response.content.decode('utf-8'))

image_sunset = os.path.join(image_dir, 'sunset.png')
response = upload_image(image_sunset, os.path.basename(image_sunset), token)
tokens.append(response.content.decode('utf-8'))

new_media_items = [{'simpleMediaItem': {'uploadToken': tok}}for tok in tokens]

request_body = {
    'newMediaItems': new_media_items
}

upload_response = service.mediaItems().batchCreate(body=request_body).execute()
