from logging import raiseExceptions
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import random

class Sticker(object):
    """
    Sticker object contains following methods
    1. to create img (sticker with text)
    2. to parse input text (if text is too long, then truncate)
    """

    positionDict = {
        "01" : (30, 20),
        # "02" : (30, 200),
        # "03" : (60, 200),
        "04" : (30, 200),
        "05" : (30, 200),
        "06" : (30, 10),
        "07" : (30, 200),
        # "08" : (30, 10),
        "09" : (30, 10),
        # "10" : (30, 200),
        # "11" : (30, 200),
        "12" : (30, 30),
        "13" : (30, 20),
        "14" : (30, 220),
        "15" : (30, 200),
        # "16" : (30, 200),
    }

    def __init__(self):
        pass

    def chooseSticker(self, text):
        """
        randomly pick a sticker
        the position of text depends on the sticker
        """
        NoList = ["01", "04", "05", "06", "07", "09", "12", "13", "14", "15"]
        stickerNO = random.sample(NoList, 1)[0]

        if stickerNO not in self.positionDict.keys():
            raiseExceptions("Sticker not supported")

        if stickerNO in ["04", "05", "06", "07", "09"]:
            textColor = (255, 255, 255) # choose white text

        if stickerNO == "13":
            text = "派出我的跟班可魯\n" + text
            textColor = (0, 0, 0) # else black
        else:
            textColor = (0, 0, 0) # else black

        self.createImg(stickerNO, text, 26, textColor)

    def createImg(self, stickerNO, text, fontsize = 26, textColor = (0, 0, 0)):
        """
        fontsize
        54 -> 約六個中文字
        26 -> 約 12 個中文字
        大於 12 個字則換行
        """
        if len(text) > 12:
            text = text[0:12] + "\n" + text[12:]

        # x & y axis
        x = self.positionDict[stickerNO][0]
        y = self.positionDict[stickerNO][1]

        # load font and choose font size
        myFont = ImageFont.truetype("./app/static/font/NotoSansTC-Regular.otf", fontsize)

        # draw img
        img = Image.open(f"./app/static/stickers/{stickerNO}.png")
        I1 = ImageDraw.Draw(img)
        I1.text((x, y), f"{text}", fill = textColor, font = myFont)

        # save
        img.save("./app/static/stickers/stickerSent.png")

sticker = Sticker()

if __name__ == "__main__":
    # print(sticker.positionDict)
    # sticker.createImg("01", "我叫琪琪，我是可愛的狗勾 我最喜歡骨頭ㄌ", 26)

    # sticker.createImg("07", "我叫琪琪，我是可愛的狗勾 我最喜歡骨頭ㄌ", 26, textColor=(255, 255, 255))
    sticker.chooseSticker("琪琪最可愛！")