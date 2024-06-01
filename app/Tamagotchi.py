from random import randrange
import random
# import googletrans

class Pet(object):
    """
    A virtual pet
    """
    food_reduce = 1
    food_max = 100
    food_warning = 20
    happiness_reduce = 1
    happiness_max = 100
    happiness_warning = 50
    excitement_reduce = 1
    excitement_max = 100
    excitement_warning = 30

    # Vocabularies
    vocab = ['敖嗚嗚嗚...', '哭哭', '我肚子餓了', '我要踢碗了ㄛ！']

    def __init__(self, name, animal_type):
        self.name = name
        self.animal_type = animal_type

        self.food = randrange(self.food_max)
        self.excitement = randrange(self.excitement_max)
        self.vocab = self.vocab[:]

    def __clock_tick(self):
        self.excitement -= 1
        self.food -= 1

    @staticmethod
    def readTextFile():
        with open("./app/vocabulary.txt", "r") as f:
            voc = f.read()
            voc = voc.split(" ")
        return voc

    @staticmethod
    def writeTextFile(textAppend):
        with open("./app/vocabulary.txt", "a") as f:
            print(" " + textAppend, file = f, end = "")

    def mood(self):
        if self.food > self.food_warning and self.excitement > self.excitement_warning:
            return "很開心～"
        elif self.food < self.food_warning:
            return "肚子餓了QQ"
        else:
            return "想要出去玩啦 > <"

    def state(self):
        self.__clock_tick()
        return "我叫 " + self.name + "，" + "\n我現在 " + self.mood() + "."

    def bark(self):
        self.__clock_tick()
        barkText = ["汪", "汪汪！", "汪汪汪！！", "你知道誰是世界上最可愛的狗狗嗎？是我！汪", "琪琪的生日才不是愚人節呢！汪", "琪琪正在思考...ㄨ..ㄤ..\n...喵～",
        "狗狗不一定是只會汪汪叫～汪！", "身為狗狗，會一點外語也是很正常的！喵", "可魯是我的後輩，只能跟在我的尾巴後面汪汪叫 汪 （身後：汪汪）"]
        return barkText[randrange(0, len(barkText))]

    def teach(self, word):
        if word == "":
            pass
        else:
            # self.vocab.append(word)
            self.writeTextFile(word)
        self.__clock_tick()

    def talk(self):
        vocab = self.readTextFile()
        self.__clock_tick()
        # print(vocab[randrange(0, len(vocab))]) 
        return vocab[randrange(0, len(vocab))]

    def feed(self):
        # meal = randrange(0, self.food_max)
        # self.food += meal
        meal = random.randint(0, 100)

        # if self.food < 0:
        if meal < 50:
            self.food = 0
            return "我肚子餓了 敖嗚嗚"

        elif self.food > self.food_max:
            # self.food = self.food_max
            self.food = random.randint(0, 100)
            return "我不想吃東西"

        return "卡茲卡茲～ \n 好ㄘ好ㄘ"
            
    def play(self):
        responseText = ['耶依～出門遛遛', '我是快樂ㄉ狗狗！', '我要去聞遍所有的電線杆', '快開門！放狗狗出去！', '我不要戴項圈QQ']
        # fun = randrange(self.excitement, self.excitement_max)
        fun = random.randint(0, 100)
        # self.excitement += fun
        # self.__clock_tick()
        # if self.excitement < 50:
        if fun < 50:
            # self.excitement = 50
            return "好無聊喔～帶我出去玩嘛\n" + responseText[randrange(0, len(responseText))]
        # elif self.excitement >= self.excitement_max:
        else:
            self.excitement = self.excitement_max
            return "我很開心～（搖尾巴）\n"  + responseText[randrange(0, len(responseText))]
    
    def sayHappyHoliday(self):
        pass


    # def translate(self, sentence, targetLang):
    #     # Initial
    #     translator = googletrans.Translator()

    #     if targetLang in ["日語", "日文", "日"]:
    #         results = translator.translate(sentence, dest='ja').text 
    #     elif targetLang in ["韓文", "韓國話", "韓"]:
    #         results = translator.translate(sentence, dest='ko').text 
    #     elif targetLang is None or targetLang in ["ENGLISH", "英文", "英"]:
    #         # Basic Translate
    #         results = translator.translate(sentence, dest='en').text
    #     else:
    #         results = translator.translate(sentence, dest='en').text 

    #     print(results)
    #     return results


# Create a new pet
class ChiChi(Pet):
    name = "琪琪"
    animal_type = "狗狗"

    def __init__(self):
        super().__init__("琪琪", "狗狗")
        # self.name = self.name
        # self.animal_type = self.animal_type
        # vocabularies = self.readTextFile()
        # self.vocab.extend(vocabularies)

    def get_vocabularies(self):
        vocabularies = self.readTextFile()
        return f"我會說這些詞彙ㄛ！不要教我說髒話\n{ ' '.join(vocabularies) }"

chichi = ChiChi()
        
if __name__ == "__main__":
    print(chichi.name)
    # chichi.bark()
    # chichi.talk()
    # chichi.teach("壞壞!!")
    # print(chichi.vocab)
    # chichi.play()
    # print(ChiChi.vocab) # not __init__ so the vocab are fewer
    # print(ChiChi.readTextFile())

    # chichi.translate("今天天氣真好","日文")
