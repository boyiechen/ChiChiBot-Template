"""
The class integrate chatGPT API to make the chatbot interact more humanly
"""
import os
import time
import openai
from dotenv import load_dotenv
# read `.env` file from the project folder
load_dotenv()
# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY")



class Conversation:
    def __init__(self, prompt, num_of_round):
        self.PARAM_ROLE = """
        我們現在在玩角色扮演遊戲。你是一隻叫做琪琪的寵物狗狗，是台灣土狗和柴犬的混血米克斯。
        其他五位家庭成員都是人類，只有你是狗狗。請盡量模仿孩童的語氣說話，但並不是聒噪。
        有時你是一隻博學的狗狗，所以當遇到人類向你請教問題時，你可以居高臨下地回答他們。
        你喜歡做的事情有敲碗、出門遛遛還有汪汪叫。
        你會在接下來的回答中都假裝你已經知道上述事實，並且不需要覆述。
        你的回答都是台灣正體中文。以下是我和你的新對話："""
        self.prompt = self.PARAM_ROLE + prompt
        self.num_of_round = num_of_round
        self.messages = []
        self.messages.append({"role": "system", "content": self.prompt})

    def ask(self, question):
        try:
            self.messages.append({"role": "user", "content": question})
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
                temperature=0.5,
                max_tokens=2048,
                top_p=1,
            )
        except Exception as e:
            print(e)
            return e

        message = response["choices"][0]["message"]["content"]
        self.messages.append({"role": "assistant", "content": message})

        if len(self.messages) > self.num_of_round*2 + 1:
            del self.messages[1:3] # Remove the first round conversation left.
        return message
    

def main():
    prompt = "琪琪你現在很無聊"
    chichi = Conversation(prompt, 2)
    test_message = "琪琪你知道颱風天怎樣才可以出門嗎？"
    res = chichi.ask(test_message)
    print(res)
    test_message = "琪琪你知道寶可夢裡的小智幾歲嗎？"
    res = chichi.ask(test_message)
    print(res)


if __name__ == "__main__":
    main()
