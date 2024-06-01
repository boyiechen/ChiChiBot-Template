import os
import pandas as pd
import pickle
import requests

from google.oauth2.service_account import Credentials
import gspread

from AccountBook import GoogleSheet
from GooglePhotosAPI.Google import Create_Service

# This script is used to concatenate LineBot and Google Photos API
"""
Methods: 

1. receive 'list album' and return table of photo albums 
2. receive 'search keyword' and return specific photo albums
3. receive 'random photo' and return random photo
4. receive img object and create shared photo album and then contain the photo

"""

# prepare the worksheet to display the list of albums
scope = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file("./app/credentials/gs_credentials.json", scopes=scope)
album_sheet_url = 'https://docs.google.com/spreadsheets/'

worksheetAlbum = GoogleSheet(scope = scope, creds = creds, sheet_url = album_sheet_url)

# The class to operate photos and albums

class GPhoto(object):

    # init Google Photos API
    def __init__(self, SERVICE, WORKSHEET):
        self.service = SERVICE
        self.worksheet = WORKSHEET
        print(self.service)

    # get the list of current albums from Google Photos 
    # update the Google Sheet
    # return the url of the sheet
    def listAlbums(self):
       # get the list of albums as a pandas df
        response = self.service.albums().list(
            pageSize=50,
            excludeNonAppCreatedData=False
        ).execute()

        lstAlbums = []
        lstAlbums.extend(response['albums'])
        while True:
            try:
                response = self.service.albums().list(
                    pageSize=50,
                    excludeNonAppCreatedData=False,
                    pageToken=response['nextPageToken']
                ).execute()
                lstAlbums.extend(response['albums'])
            except KeyError:
                break        
        df_albums = pd.DataFrame(lstAlbums)


        # we can get the shareableUrl of the album if it is created by API and turned on share setting
        shareableUrls = []
        for index, item in enumerate(df_albums['shareInfo']):
            try:
                shareableUrls.append(item['shareableUrl'])
            except:
                shareableUrls.append(str(""))
        df_albums['shareableUrl'] = shareableUrls
        # print()
        # print(">>> The following is the shareable urls")
        # print(shareableUrls)
        # print(">>> ends")
        # print()

        try:
            df_albums.drop('shareInfo', inplace=True, axis=1) # since shareInfo contains python diction format, making the update method of sheet API not working
        except:
            pass
        df_albums = df_albums.fillna('')
        df_albums = df_albums.sort_values('title')
        df_albums = df_albums.reset_index(drop=True)
        df_albums = df_albums[['title', 'shareableUrl', 'mediaItemsCount']]
        print(df_albums)
        # write table
        # df_albums.to_excel("./app/db/albums.xlsx")
        # maybe we need to delete all record and then fill out
        # instead of replace
        self.worksheet.replaceRecord(df_albums)

        res = {
            "table" : df_albums,
            "url"   : "https://docs.google.com/spreadsheets/d/1fYh52iPEBQjvMXGbctHJqMnjnBLGMz1EnuZ8vwIDc40/edit?usp=sharing"
        }
        return res

    # get album by album ID
    def getAlbum(self, ID):
        response = self.service.albums().get(albumId=ID).execute()
        return response


    # return the title and the url of specific albums
    def searchAlbumByTitle(self, keyword):
        df = self.listAlbums()['table']
        df = df[  df['title'].str.contains(keyword) ]
        if df.shape[0] == 0:
            raise Exception("Album titles do not contain current keyword.")

        df = df[['title', 'shareableUrl']].reset_index(drop=True)
        return df

    
    # create album with title and sharing setting
    def initAlbum(self, albumTitle):
        df = self.listAlbums()['table']
        n_albums = df.shape[0]
        event_prefix = f"{n_albums}"

        # create empty album with given title
        request_body = {
            'album': {'title': f'{event_prefix}_{albumTitle}'}
        }
        # request_body = {
        #     'album': {'title': f'{albumTitle}'}
        # }
        
        responseAlbum = self.service.albums().create(body=request_body).execute()
        # edit sharing setting
        request_body = {
            'sharedAlbumOptions': {
                'isCollaborative': True,
                'isCommentable': True
            }
        }
        responseSharedAlbum = self.service.albums().share(
            albumId = responseAlbum['id'],
            body = request_body
        ).execute()
        

        return [responseAlbum, responseSharedAlbum]

    # check the tmp photos
    @staticmethod
    def listTempImg():
        photos = os.listdir("./app/static")
        # print(photos)
        # photos = [ "./app/static" + p for p in photos]
        # print(photos)
        return photos


    # a method to be called afterwhile
    @staticmethod
    def uploadImage(image_path, upload_file_name, token):
        upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
        headers = {
            'Authorization': 'Bearer ' + token.token,
            'Content-type': 'application/octet-stream',
            'X-Goog-Upload-Protocol': 'raw',
            'X-Goog-File-Name': upload_file_name
        }    

        img = open(image_path, 'rb').read()
        response = requests.post(upload_url, data=img, headers=headers)
        try:
            print('\nUpload token: {0}'.format(response.content.decode('utf-8')))
        except:
            pass
        # print()
        # print("The following is the first response")
        # print(response)
        # print()
        return response


    # upload photo into given albums
    def batchUploadImg(self, ImgNameList, albumID):

        # collect the imgs that are uploaded afterwhile
        tokens = []
        image_dir = os.path.join(os.getcwd(), 'app/static')
        upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
        token = pickle.load(open('token_photoslibrary_v1.pickle', 'rb'))

        # create tokens
        for img_name in ImgNameList:
            path = os.path.join(image_dir, img_name)
            response = self.uploadImage(path, img_name, token)
            tokens.append(response.content.decode('utf-8'))

        # form request body
        new_media_items = [{'simpleMediaItem': {'uploadToken': tok}}for tok in tokens]
        request_body = {
            'albumId' : albumID,
            'newMediaItems': new_media_items
        }
        # upload
        upload_response = self.service.mediaItems().batchCreate(body=request_body).execute()
        # print()
        # print("The following is the second response")
        # print(upload_response)
        # print()

    # after upload photos, clean up the temp photos
    def removeImg(self):
        imgs = self.listTempImg()
        image_dir = os.path.join(os.getcwd(), 'app/static')
        for img in imgs:
            path = os.path.join(image_dir, img)
            os.remove(path)


    


# TEST
if __name__ == "__main__":
    API_NAME = 'photoslibrary'
    API_VERSION = 'v1'
    CLIENT_SECRET_FILE = './app/credentials/gphoto_client_secret.json'
    SCOPES = ['https://www.googleapis.com/auth/photoslibrary.sharing',
            'https://www.googleapis.com/auth/photoslibrary',
            'https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata']
    # service = Create_Service(CLIENT_SECRET_FILE,API_NAME, API_VERSION, SCOPES)
    googlePhoto = GPhoto(SERVICE=Create_Service(CLIENT_SECRET_FILE,API_NAME, API_VERSION, SCOPES), 
                         WORKSHEET=worksheetAlbum)

    # test list method
    googlePhoto.listAlbums()
    
    # test get method
    # album_id = ""
    # print(googlePhoto.getAlbum(ID = album_id))

    # test search method
    print(googlePhoto.searchAlbumByTitle("週五"))
    # df = googlePhoto.searchAlbumByTitle("")
    # print(df.shape[0])

    # # test initAlbum() method
    res = googlePhoto.initAlbum("這是測試相簿啦！")
    for item in res:
        print()
        print(item)
        print()
    print(res[0]['id'])

    # test listTempImg() and upload method
    ThisIsAnImgList = googlePhoto.listTempImg()
    ThisIsAlbumID = res[0]['id']
    googlePhoto.batchUploadImg(ThisIsAnImgList, ThisIsAlbumID)

    print("Successfuly upload imgs to specific album")

    # test rm
    googlePhoto.removeImg()
