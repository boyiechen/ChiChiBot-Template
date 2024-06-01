import os
import re
import requests
import base64
import json
from requests.structures import CaseInsensitiveDict

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

# use flex message
# from linebot.models import FlexSendMessage
from linebot.models.flex_message import (
    BubbleContainer, ImageComponent
)
from linebot.models.actions import URIAction

from config import *
from AccountBook import GoogleSheet
from AccountBook import CurrencyConverter
from tools import Analysis
from Tamagotchi import ChiChi
from GPhotoTools import GPhoto
from GooglePhotosAPI.Google import Create_Service


# AzureAI影像服務相關套件
from azure.cognitiveservices.vision.face import FaceClient
from azure.cognitiveservices.vision.face.models import TrainingStatusType
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from AzureAPI import Azure

# chatGPT API
import openai
from dotenv import load_dotenv
# read `.env` file from the project folder
load_dotenv()
# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY")
from chatGPT import Conversation


# Sticker class
from stickers.Sticker import sticker

app = Flask(__name__)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
        # handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

"""
add text message handler
"""
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    chichi = ChiChi()
    random_setting = chichi.talk()
    chichichat = Conversation(random_setting, 10)

    # Tamagotchi part
    if event.message.text[:3] == "琪琪叫":
        text = chichi.bark()
        message = TextSendMessage(text = text)
        line_bot_api.reply_message(event.reply_token, message)

    if event.message.text == "琪琪":
        text = chichi.talk()
        message = TextSendMessage(text = text + " 怎麼了～")
        line_bot_api.reply_message(event.reply_token, message)

    elif event.message.text[:3] == "琪琪說":
        chichi.teach(event.message.text[3:])
        text = chichi.talk()
        message = TextSendMessage(text = text)
        line_bot_api.reply_message(event.reply_token, message)
    
    elif event.message.text == "琪琪最可愛":
        text = chichi.talk()

        # 上傳sticker照片至imgur
        azure = Azure(Azure_COMPUTER_VISION_KEY, Azure_COMPUTER_VISION_ENDPOINT, imgur_client_id, imgur_client_secret)
        imgurUrl = azure.uploadImg(path = os.path.join(os.getcwd(), 'app/stickers'), filename = "ChiChiCute.png")

        image_message = ImageSendMessage(
            original_content_url=imgurUrl,
            preview_image_url=imgurUrl
        )
        message = TextSendMessage(text = text)

        line_bot_api.reply_message(event.reply_token, [message, image_message])

    elif event.message.text == "琪琪不要說":
        text = chichi.talk()
        print(text)
        sticker.chooseSticker(text)

        # 上傳sticker照片至imgur
        azure = Azure(Azure_COMPUTER_VISION_KEY, Azure_COMPUTER_VISION_ENDPOINT, imgur_client_id, imgur_client_secret)
        imgurUrl = azure.uploadImg(path = os.path.join(os.getcwd(), 'app/stickers'), filename = "stickerSent.png")

        image_message = ImageSendMessage(
            original_content_url=imgurUrl,
            preview_image_url=imgurUrl
        )
        message = TextSendMessage(text = "不讓我說，我就用寫字的！")

        line_bot_api.reply_message(event.reply_token, [message, image_message])
    
    elif event.message.text[:3] == "琪琪玩":
        text = chichi.play()
        message = TextSendMessage(text = text)
        line_bot_api.reply_message(event.reply_token, message)

    elif event.message.text == "琪琪自我介紹":
        text = chichi.state()
        message = TextSendMessage(text = text)
        line_bot_api.reply_message(event.reply_token, message)

    elif event.message.text == "琪琪會說什麼":
        text = chichi.get_vocabularies()
        message = TextSendMessage(text = text)
        line_bot_api.reply_message(event.reply_token, message)

    elif event.message.text[:3] == "琪琪吃":
        text = chichi.feed()
        message = TextSendMessage(text = text)
        line_bot_api.reply_message(event.reply_token, message)

    # else:
    #     text = chichi.bark() + f"我會說這些詞彙ㄛ！不要教我說髒話\n{ ' '.join(chichi.vocab) }"
    #     message = TextSendMessage(text = text)
    #     line_bot_api.reply_message(event.reply_token, message) 

    # chatGPT part
    elif event.message.text[:5] == "聰明的琪琪":
        text = event.message.text[5:]
        message = TextSendMessage(text = chichichat.ask(text))
        line_bot_api.reply_message(event.reply_token, message)


    # Account Book Part
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file("./app/credentials/gs_credentials.json", scopes=scope)
    sheet_url = 'https://docs.google.com/spreadsheets/'
    accountBook = GoogleSheet(scope, creds, sheet_url)

    # expense or income
    if event.message.text[:2] in ["支出", "收入"]:
        try:
            record = accountBook.convertText(event.message.text)
            df = accountBook.createRecord(record)
            accountBook.writeRecord(df)
            message = TextSendMessage(text = "Successfully add record!!")
            line_bot_api.reply_message(event.reply_token, message)
        except ValueError as e:
            message = TextSendMessage(text = str(e))
            line_bot_api.reply_message(event.reply_token, message) 
            

    # list the 10 latest records
    elif event.message.text[:2] == "查詢":
        df = accountBook.readRecord(length = 10)
        message = TextSendMessage(text=str(df)) # make the text string become a certain class that can be passed by the API
        line_bot_api.reply_message(event.reply_token, message)
    
    elif event.message.text == "google sheet":
        sheet_url = "https://docs.google.com/spreadsheets/"
        message = TextSendMessage(text=sheet_url) # make the text string become a certain class that can be passed by the API
        line_bot_api.reply_message(event.reply_token, message) 

    # delete the last record
    elif event.message.text[:5] == "刪除上一筆":
        try:
            df = accountBook.deleteRecord()
            message = TextSendMessage(text="已經刪除此筆紀錄:\n {foo} ".format(foo=str(df))) # make the text string become a certain class that can be passed by the API
            line_bot_api.reply_message(event.reply_token, message)
        except Exception as e:
            message = TextSendMessage(text = str(e))
            line_bot_api.reply_message(event.reply_token, message)


    # look up for exchange rate
    elif re.search("兌換", event.message.text):
        try:
            # get the wanted currencies
            country1, country2 = CurrencyConverter.convertText(text_string = event.message.text)
            # find the rate
            rate = CurrencyConverter(country1, country2).rate
            rate_inv = CurrencyConverter(country2, country1).rate 
            # return result
            message = TextSendMessage(text = f"{country1}兌換{country2}匯率為 1 : {rate} \n{country2}兌換{country1}匯率為 1 : {rate_inv}")
            line_bot_api.reply_message(event.reply_token, message)
        except Exception as e:
            message = TextSendMessage(text = str(e))
            line_bot_api.reply_message(event.reply_token, message)
    
    elif event.message.text[:2] == "餘額":
        monthlyBalance = Analysis.balance(accountBook.worksheet)
        message = TextSendMessage(text = f"Statistics from {str(monthlyBalance['start_date'])} to {str(monthlyBalance['end_date'])} \nCurrent balance is: {monthlyBalance['balance']} NTD\nAverage daily cost is about {monthlyBalance['average_daily_cost']} NTD")
        line_bot_api.reply_message(event.reply_token, message)

    elif event.message.text == "總餘額":
        monthlyBalance = Analysis.totalBalance(accountBook.worksheet)
        message = TextSendMessage(text = f"Statistics from {str(monthlyBalance['start_date'])} to {str(monthlyBalance['end_date'])} \nCurrent balance is: {monthlyBalance['balance']} NTD\nAverage daily cost is about {monthlyBalance['average_daily_cost']} NTD")
        line_bot_api.reply_message(event.reply_token, message)

    elif event.message.text == "測試":
        flex_message = FlexSendMessage(
            alt_text='我的部落格',
            contents=BubbleContainer(
                direction='ltr',
                hero=ImageComponent(
                    url='',
                    size='full',
                    aspect_ratio='20:13',
                    aspect_mode='cover',
                    action=actions.URIAction(uri='https://boyie.net', label='label')
                )
            )
        )
        line_bot_api.reply_message(event.reply_token, flex_message)



    # Google Photo Operation Part
    worksheetAlbum = GoogleSheet(scope = ['https://www.googleapis.com/auth/spreadsheets'], 
                                 creds = Credentials.from_service_account_file("./app/credentials/gs_credentials.json", scopes=scope), 
                                 sheet_url = '')
    API_NAME = 'photoslibrary'
    API_VERSION = 'v1'
    CLIENT_SECRET_FILE = './app/credentials/gphoto_client_secret.json'
    SCOPES = ['https://www.googleapis.com/auth/photoslibrary.sharing',
            'https://www.googleapis.com/auth/photoslibrary',
            'https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata']
    googlePhoto = GPhoto(SERVICE=Create_Service(CLIENT_SECRET_FILE,API_NAME, API_VERSION, SCOPES), 
                         WORKSHEET=worksheetAlbum)
    if event.message.text == "相簿":
        res = googlePhoto.listAlbums()['url']
        message = TextSendMessage(text = res)
        line_bot_api.reply_message(event.reply_token, message)
    
    elif re.search("查詢相簿|搜尋相簿|找相簿", event.message.text):
        keyword = re.sub("查詢相簿|搜尋相簿|找相簿", "", event.message.text)
        res = googlePhoto.searchAlbumByTitle(keyword)
        # message = TextSendMessage(text = "heyhey")
        message = TextSendMessage(text = repr(res))
        line_bot_api.reply_message(event.reply_token, message)

    elif event.message.text == "琪琪不用上傳這些照片":
        content = TextSendMessage(text = "琪琪覺得你的照片拍得真好！")
        line_bot_api.reply_message(event.reply_token, content)
        # clean up tmp photos
        googlePhoto.removeImg()

    elif event.message.text == "琪琪幫我在 google photo 上傳這些照片並建立相簿":
        # ask user the album title
        content = TextSendMessage(text = "琪琪問你～要幫相簿取什麼標題呢？\n請以「相簿名稱是」來開頭喔！\n例如「相簿名稱是琪琪真可愛！」")
        line_bot_api.reply_message(event.reply_token, content)

    elif event.message.text[0:5] == "相簿名稱是":
        print(googlePhoto.listAlbums()['url'])
        # initialize an album with given name
        res = googlePhoto.initAlbum(albumTitle=event.message.text[5:])

        # get the album id
        albumID = res[0]['id']

        # upload img to the specific album
        imgs_to_upload = googlePhoto.listTempImg()
        googlePhoto.batchUploadImg(imgs_to_upload, albumID)

        # get the album
        albumCreated = googlePhoto.getAlbum(albumID)
        albumLink = albumCreated['shareInfo']['shareableUrl']

        # repr(albumCreated)
        print(albumCreated)
        message = TextSendMessage(text = f"相簿建立好囉！連結是：{albumLink}")
        line_bot_api.reply_message(event.reply_token, message)

        # clean up tmp photos
        googlePhoto.removeImg()

    # Instruction Part
    # else:
    #     content = TextSendMessage(text = "琪琪可以幫你上傳照片到 Google 相簿喔！傳一張或多張照片上來試試吧！")
    #     line_bot_api.reply_message(event.reply_token, content)



"""
add image message handler
"""
@handler.add(MessageEvent, message=ImageMessage)
def handle_Message(event):
    # if user send photos, guess that users want to create an album and upload them
    if (event.message.type == "image"):

        # save the temporary photos, and wait for the response
        url = f"https://api-data.line.me/v2/bot/message/{event.message.id}/content"
        headers = CaseInsensitiveDict()
        headers["Authorization"] = f"Bearer {channel_access_token}"
        
        resp = requests.get(url, headers=headers, stream = True)
        # print(resp.status_code)
        path = f"./app/static/{event.message.id}.jpg"
        # path = f"{os.getcwd(), '/app/static'}/{event.message.id}.jpg"
        # print(path)
        content = base64.b64encode(resp.content)

        if resp.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)

        # if there is only one img
        # use the azure computer vision API
        if event.message.image_set is None:
            pass
            
        #     # 建立 message payload
        #     toReply = []
        #     # Azure Client
        #     azure = Azure(Azure_COMPUTER_VISION_KEY, Azure_COMPUTER_VISION_ENDPOINT, imgur_client_id, imgur_client_secret)

        #     # 接收到使用者傳送的原始照片
        #     message_content = line_bot_api.get_message_content(event.message.id)
        #     # 照片儲存名稱
        #     fileName = event.message.id + '.jpg'
        #     # pathName = './app/static/' + event.message.id + '.jpg'
        #     pathName = os.path.join(os.getcwd(), 'app/static', fileName)
        #     # 儲存照片至本地端
        #     with open(pathName, 'wb')as f:
        #         for chunk in message_content.iter_content():
        #             f.write(chunk)
        #     # 上傳原始照片至imgur
        #     # imgurUrl = azure.uploadImg(path = "./app/static", filename = fileName)
        #     imgurUrl = azure.uploadImg(path = os.path.join(os.getcwd(), 'app/static'), filename = fileName)

        #     # # 執行Azure物件辨識
        #     # azure.AzureCV(imgurUrl)
        #     # img_url = azure.uploadImg(path = "./app/AzureAPI/output", filename= "output.png")
        #     # image_message = ImageSendMessage(
        #     #     original_content_url = img_url,
        #     #     preview_image_url = img_url
        #     #     )
        #     # # line_bot_api.reply_message(event.reply_token, image_message)
        #     # toReply.append(image_message)


        #     # 執行Azure OCR
        #     ocrResult = azure.OCR(img_url=imgurUrl, img_filepath = pathName)
        #     # 若有辨識出OCR字元 則回傳結果給使用者
        #     if len(ocrResult['ocrText']) != 0:
        #         # 組合ocr字元
        #         ocrText = ocrResult['ocrText']
        #         ocrText = '\n'.join(ocrText)
        #         ocrText = f"琪琪幫你找出這裡的文字！嗅嗅～(聞) {ocrText}"
        #         ocrImg = ocrResult['ocrImg_url']

        #         # 讀取flex message格式
        #         bubble = json.load(open("./app/flexMsgTemplate.json", 'r'))
        #         bubble["hero"]["url"] = ocrImg
        #         bubble["hero"]["action"]["uri"] = ocrImg
        #         bubble["body"]["contents"][0]["text"] = ocrText

        #         # linebot回傳flex message
        #         # line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="Report", contents=bubble))
        #         flexmsgOCR = FlexSendMessage(alt_text="Report", contents=bubble)
        #         toReply.append(flexmsgOCR)


        #     # 執行Azure圖片描述
        #     describleText = azure.describeImg(imgurUrl)
        #     if describleText:
        #         describleText = f"琪琪覺得這張照片描述的是...嗅嗅～（用力聞） {describleText}"   
        #         # 讀取flex message格式
        #         bubble = json.load(open("./app/flexMsgTemplate.json", 'r'))
        #         bubble["hero"]["url"] = imgurUrl
        #         bubble["hero"]["action"]["uri"] = imgurUrl
        #         bubble["body"]["contents"][0]["text"] = describleText

        #         # linebot回傳flex message
        #         # line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="Report", contents=bubble))
        #         flexmsgDesc = FlexSendMessage(alt_text="Report", contents=bubble)
        #         toReply.append(flexmsgDesc)
        #     line_bot_api.reply_message(event.reply_token, toReply)
            
        #     # remove photos
        #     image_dir = os.path.join(os.getcwd(), 'app/static')
        #     for img in os.listdir("./app/static"):
        #         path = os.path.join(image_dir, img)
        #         os.remove(path)

        # # if there is only one img
        # if event.message.image_set is None:
        #     welcomeText = "琪琪問你～你想要上傳這張照片並建立相簿嗎？\n1. 不用\n2. 對，這些就是我要上傳的照片\n3. 對，我還要從手機相簿選取照片上傳\n4. 對，我還要開啟相機拍攝照片上傳"
        #     line_bot_api.reply_message(
        #         event.reply_token,
        #         TextSendMessage(
        #             text= welcomeText,
        #             quick_reply=QuickReply(
        #                 items=[
        #                     QuickReplyButton(
        #                         action=MessageAction(label="1.不用", text="琪琪不用上傳這些照片")
        #                     ),
        #                     QuickReplyButton(
        #                         action=MessageAction(label="2.建立相簿", text="琪琪幫我在 google photo 上傳這些照片並建立相簿")
        #                     ),
        #                     QuickReplyButton(
        #                         action=CameraAction(label="3.開啟相機")
        #                     ),
        #                     QuickReplyButton(
        #                         action=CameraRollAction(label="4.選取手機相簿照片")
        #                     ),]
        #                 )
        #             )
        #         )
        # if there are multiple img, consider creating an album
        elif event.message.image_set.index == 1:
            welcomeText = "琪琪問你～你想要上傳這些照片並建立相簿嗎？\n1. 不用\n2. 對，這些就是我要上傳的照片\n3. 對，我還要從手機相簿選取照片上傳\n4. 對，我還要開啟相機拍攝照片上傳"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text= welcomeText,
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyButton(
                                action=MessageAction(label="1.不用", text="琪琪不用上傳這些照片")
                            ),
                            QuickReplyButton(
                                action=MessageAction(label="2.建立相簿", text="琪琪幫我在 google photo 上傳這些照片並建立相簿")
                            ),
                            QuickReplyButton(
                                action=CameraAction(label="3.開啟相機")
                            ),
                            QuickReplyButton(
                                action=CameraRollAction(label="4.選取手機相簿照片")
                            ),]
                        )
                    )
                )

            # # save the temporary photos, and wait for the response
            # url = f"https://api-data.line.me/v2/bot/message/{event.message.id}/content"
            # headers = CaseInsensitiveDict()
            # headers["Authorization"] = f"Bearer {channel_access_token}"
            
            # resp = requests.get(url, headers=headers, stream = True)
            # # print(resp.status_code)
            # path = f"./app/static/{event.message.id}.jpg"
            # # path = f"{os.getcwd(), '/app/static'}/{event.message.id}.jpg"
            # # print(path)
            # content = base64.b64encode(resp.content)

            # if resp.status_code == 200:
            #     with open(path, 'wb') as f:
            #         for chunk in resp.iter_content(1024):
            #             f.write(chunk)



if __name__ == "__main__":
    # production
    # port = int(os.environ.get('PORT', 33507))
    # app.run(host='0.0.0.0', port=port, debug=False)

    # debug    
    app.run(port=5000, debug=True)
