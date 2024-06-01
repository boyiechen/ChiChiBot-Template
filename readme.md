# Description

ChiChiBot is a linebot for family usage in the line group chat.

# Main Feathures

1. Account Book Entry
  * write, read, delete records
  * real exchange rate
  * analysis
2. Tamagotchi
  * text message interaction with the tamagotchi
  * sticker interaction (TBA)
3. Combination of Google Photos API and Line chat
  * list albums
  * create album and upload images
  * display random photos (TBA)

# Deployment

* always remember to create the following folder
1. `app/static`
2. `app/AzureAPI/output`

# Structure

```bash
.
├── Procfile
├── app
│   ├── AccountBook.py
│   ├── GPhotoTools.py
│   ├── GooglePhotosAPI
│   │   ├── Google.py
│   │   ├── __pycache__
│   │   │   ├── Google.cpython-39.pyc
│   │   │   └── init_photo_service.cpython-39.pyc
│   │   ├── albums.py
│   │   ├── batchCreate.py
│   │   ├── init_photo_service.py
│   │   └── mediaItems.py
│   ├── Tamagotchi.py
│   ├── __init__.py
│   ├── config.py
│   ├── credentials
│   │   ├── gphoto_client_secret.json
│   │   └── gs_credentials.json
│   ├── db
│   │   ├── albums.xlsx
│   │   └── mediaItems.xlsx
│   ├── img_upload
│   │   └── test.jpg
│   ├── static
│   ├── templates
│   │   └── Tamagotchi_template.py
│   └── tools.py
├── clock.py
├── readme.md
├── requirements.txt
├── runtime.txt
└── token_photoslibrary_v1.pickle
```


## Example of configuration files

```python
# config.py

from google.oauth2.service_account import Credentials
# line-bot
channel_access_token = "YOUR_LINEBOT_CHANNEL_ACCESS_TOKEN"
channel_secret = "YOUR_LINEBOT_CHANNEL_SECRET"

# exchange rate api
# "https://v6.exchangerate-api.com/v6/"
exchange_rate_API_key = "API_KEY"
```


```json
// gs_credentials.json
{
  "type": "",
  "project_id": "",
  "private_key_id": "",
  "private_key": "",
  "client_email": "",
  "client_id": "",
  "auth_uri": "",
  "token_uri": "",
  "auth_provider_x509_cert_url": "",
  "client_x509_cert_url": ""
}
```
