from logging import raiseExceptions
import os
from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import pyimgur
from config import *
# from config import Azure_COMPUTER_VISION_KEY
# from config import Azure_COMPUTER_VISION_ENDPOINT

from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes

# 匯入必要套件，主要都是跟讀檔、繪圖和 Azure 的相關套件 

# 一開始除了匯入套件以外，還需要利用金鑰SUBSCRIPTION_KEY和端點ENDPOINT，取得使用電腦視覺服務的權限。

class Azure:

    def __init__(self, Azure_COMPUTER_VISION_KEY, Azure_COMPUTER_VISION_ENDPOINT, imgur_client_id, imgur_client_secret):
        self.SUBSCRIPTION_KEY = Azure_COMPUTER_VISION_KEY
        self.ENDPOINT = Azure_COMPUTER_VISION_ENDPOINT
        self.CV_CLIENT = ComputerVisionClient(
            self.ENDPOINT, CognitiveServicesCredentials(self.SUBSCRIPTION_KEY)
            )
        self.imgur_client_id = imgur_client_id
        self.imgur_client_secret = imgur_client_secret

    def uploadImg(self, path, filename):
        im = pyimgur.Imgur(self.imgur_client_id)
        uploaded_img = im.upload_image(f"{path}/{filename}", title = filename)

        # print(uploaded_img.title)
        print(uploaded_img.link)
        # print(uploaded_img.size)
        # print(uploaded_img.type)
        img_url = uploaded_img.link
        return img_url
        

    def AzureCV(self, img_url):
        """
        Azure object detection
        """
        
        # 透過圖片的 URL 取得圖片
        url = img_url
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        
        # 開始設定繪圖相關的部分，由於會需要在圖片上寫字，需要準備字型檔
        draw = ImageDraw.Draw(img)
        font_size = int(5e-2 * img.size[1])
        fnt = ImageFont.truetype("./app/AzureAPI/NotoSansTC-Regular.otf", size=font_size)
        # 透過電腦視覺的功能取得物件，偵測的結果會包含匡出物體的左上角座標(x, y)，以及方匡的寬跟高(w, h)，過這四個值即可畫出方匡，並且標示辨識結果以及辨識的信心程度。
        object_detection = self.CV_CLIENT.detect_objects(url)
        if len(object_detection.objects) > 0:
            for obj in object_detection.objects:
                left = obj.rectangle.x
                top = obj.rectangle.y
                right = obj.rectangle.x + obj.rectangle.w
                bot = obj.rectangle.y + obj.rectangle.h
                name = obj.object_property
                confidence = obj.confidence
                print("{} at location {}, {}, {}, {}".format(name, left, right, top, bot))
                draw.rectangle([left, top, right, bot], outline=(255, 0, 0), width=3)
                draw.text(
                    [left, top + font_size],
                    "{0} {1:0.1f}".format(name, confidence * 100),
                    fill=(255, 0, 0),
                    font=fnt,
                )
        # 最後存檔
        img.save("./app/AzureAPI/output/output.png")
        print("Done!")
        print("Please check ouptut.png")



    def OCR(self, img_url, img_filepath):
        # 開始進行OCR字元辨識
        ocr_results = self.CV_CLIENT.read(img_url, raw=True)
        operation_location_remote = ocr_results.headers["Operation-Location"]
        operation_id = operation_location_remote.split("/")[-1]

        # 偵測OCR字元辨識是否已執行完畢
        status = ["notStarted", "running"]
        while True:
            get_handw_text_results = self.CV_CLIENT.get_read_result(operation_id)
            if get_handw_text_results.status not in status:
                break
            # time.sleep(1)

        ocrText = []  # 存放OCR的辨識文字
        if get_handw_text_results.status == OperationStatusCodes.succeeded:

            # 讀取實際照片
            img = Image.open(img_filepath)
            draw = ImageDraw.Draw(img)

            res = get_handw_text_results.analyze_result.read_results
            for text_result in res:
                for line in text_result.lines:
                    ocrText.append(line.text)
                    bounding_box = line.bounding_box
                    bounding_box += bounding_box[:2]
                    draw.line(line.bounding_box, fill=(255, 0, 0), width=2)

        # 儲存處理好的照片
        try:
            saveFileName = './app/AzureAPI/output/output_ocr.jpg'
            img.save(saveFileName)
            # 將處理好的照片傳至imgur
            img_url = self.uploadImg(path = './app/AzureAPI/output', filename = "output_ocr.jpg")
        except:
            saveFileName = './app/AzureAPI/output/output_ocr.png'
            img.save(saveFileName)
            # 將處理好的照片傳至imgur
            img_url = self.uploadImg(path = './app/AzureAPI/output', filename = "output_ocr.png")

        return {
            'ocrText' : ocrText,
            'ocrImg_url' : img_url,
        }

    def describeImg(self, img_ur):
        # 開始進行圖片描述
        description_results = self.CV_CLIENT.describe_image(img_ur)
        describleText = ""
        for caption in description_results.captions:
        
            describleText += "'{}' with confidence {:.2f}% \n".format(caption.text, caption.confidence * 100)
        
        return describleText

if __name__ == "__main__":
    azure = Azure(Azure_COMPUTER_VISION_KEY, Azure_COMPUTER_VISION_ENDPOINT, imgur_client_id, imgur_client_secret)

    ## test img recognition
    # print(azure.imgur_client_id)
    img_url = azure.uploadImg(path = "./app/static", filename = "test1.png")
    # azure.AzureCV(img_url)
    # img_url = azure.uploadImg(path = "./app/AzureAPI/output", filename= "output.png")

    ## test OCR
    mydict = azure.OCR(img_url=img_url, img_filepath="./app/static/test1.png")
    if mydict:
        print(mydict['ocrText'], mydict['ocrImg_url'])

    ## test describe
    res = azure.describeImg(img_url)
    print(res)
