"""
The class integrate chatGPT API to make the chatbot interact more humanly
"""
import os
import time
import openai
import sqlite3
from linebot.v3.messaging import QuickReply, QuickReplyItem, PostbackAction, TextMessage
from config import OPENAI_API_KEY, SQLITE_DB_PATH, CHATBOT_ROLE_DESCRIPTION, CHATBOT_NAME, CHATBOT_SPECIES
openai.api_key = OPENAI_API_KEY


class Conversation:
    def __init__(self, user_id, prompt, num_of_round, group_id=None):
        self.PARAM_NAME = CHATBOT_NAME
        self.PARAM_SPECIES = CHATBOT_SPECIES
        self.PARAM_ROLE = CHATBOT_ROLE_DESCRIPTION

        self.user_id = user_id
        self.prompt = self.PARAM_ROLE + prompt
        self.num_of_round = num_of_round
        self.messages = []
        self.messages.append({"role": "system", "content": self.prompt})

        self.conn = sqlite3.connect(SQLITE_DB_PATH)
        self.c = self.conn.cursor()
        self.load_user_relationship()
        self.load_recent_conversation_history(group_id)

    def load_user_relationship(self):
        self.c.execute("SELECT relationship FROM authorized_users WHERE user_id = ?", (self.user_id,))
        row = self.c.fetchone()
        self.relationship = row[0] if row else 'Unknown'
        self.messages.append({"role": "system", "content": f"The user talking to you is {self.relationship}."})

    def load_recent_conversation_history(self, group_id):
        if group_id:
            self.c.execute(f"SELECT role, content FROM recent_conversations WHERE group_id = ? ORDER BY timestamp DESC LIMIT {self.num_of_round}", (group_id,))
        else:
            self.c.execute(f"SELECT role, content FROM recent_conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT {self.num_of_round}", (self.user_id,))
        rows = self.c.fetchall()
        for row in reversed(rows):  # Load in the correct order
            self.messages.append({"role": row[0], "content": row[1]})

    def save_message(self, role, content, context=None, score=None):
        self.c.execute("INSERT INTO conversations (user_id, role, content, context, score) VALUES (?, ?, ?, ?, ?)", 
                    (self.user_id, role, content, context, score))
        self.conn.commit()
        return self.c.lastrowid  # Return the ID of the inserted message

    def save_recent_message(self, role, content, group_id):
        self.c.execute("INSERT INTO recent_conversations (user_id, role, content, group_id) VALUES (?, ?, ?, ?)", 
                    (self.user_id, role, content, group_id))
        self.conn.commit()
        # Keep only the last 100 messages per user/group
        self.c.execute("""
            DELETE FROM recent_conversations 
            WHERE user_id = ? AND (group_id = ? OR group_id IS NULL) AND id NOT IN (
                SELECT id FROM recent_conversations WHERE user_id = ? AND (group_id = ? OR group_id IS NULL) ORDER BY timestamp DESC LIMIT 100
            )
        """, (self.user_id, group_id, self.user_id, group_id))
        self.conn.commit()


    def ask(self, question, group_id):
        try:
            self.messages.append({"role": "user", "content": question})
            self.save_message("user", question)
            # self.save_recent_message("user", question, group_id)
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
        reply_id = self.save_message("assistant", message, context=question)  # Get the reply_id here
        self.save_recent_message("assistant", message, group_id)

        if len(self.messages) > self.num_of_round * 2 + 1:
            del self.messages[1:3]  # Remove the first round conversation left.

        quick_reply = QuickReply(items=[
            QuickReplyItem(action=PostbackAction(label=f"{self.PARAM_NAME}的回答很棒！", data=f"chatgpt_good,{reply_id}")),
            QuickReplyItem(action=PostbackAction(label=f"{self.PARAM_NAME}的回答普普", data=f"chatgpt_neutral,{reply_id}")),
            QuickReplyItem(action=PostbackAction(label=f"{self.PARAM_NAME}你在亂講！壞{self.PARAM_SPECIES}！", data=f"chatgpt_bad,{reply_id}"))
        ])

        return TextMessage(text=message, quick_reply=quick_reply)

    def __del__(self):
        self.conn.close()

def update_score(reply_id, score):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE conversations SET score = ? WHERE id = ?", (score, reply_id))
    conn.commit()
    conn.close()

