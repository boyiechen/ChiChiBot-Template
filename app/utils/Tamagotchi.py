import random
import sqlite3
from datetime import datetime, timedelta
from icecream import ic
from config import SQLITE_DB_PATH

class Pet:
    def __init__(self, name, animal_type):
        self.name = name
        self.animal_type = animal_type
        self.food = random.randint(0, 100)
        self.excitement = random.randint(0, 100)
        self.happiness = random.randint(0, 100)
        self.last_interaction = datetime.now()
        self.create_table_if_not_exists()
        self.load_state()

    def create_table_if_not_exists(self):
        with self.get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS tamagotchi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    animal_type TEXT NOT NULL,
                    food INTEGER NOT NULL,
                    excitement INTEGER NOT NULL,
                    happiness INTEGER NOT NULL,
                    last_interaction DATETIME NOT NULL
                )
            ''')
            conn.commit()

    def get_db_connection(self):
        return sqlite3.connect(SQLITE_DB_PATH)

    def load_state(self):
        with self.get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT food, excitement, happiness, last_interaction FROM tamagotchi WHERE name = ?", (self.name,))
            row = c.fetchone()
            if row:
                self.food, self.excitement, self.happiness, last_interaction_str = row
                self.last_interaction = datetime.strptime(last_interaction_str, "%Y-%m-%d %H:%M:%S.%f")
            else:
                self.save_state(conn)  # Save initial state if not in database

    def save_state(self, conn=None):
        if conn is None:
            conn = self.get_db_connection()
        with conn:
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO tamagotchi (name, animal_type, food, excitement, happiness, last_interaction)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.name, self.animal_type, self.food, self.excitement, self.happiness, self.last_interaction))
            conn.commit()

    def clock_tick(self):
        now = datetime.now()
        if (now - self.last_interaction) > timedelta(minutes=1):
            self.food = max(0, self.food - 1)
            self.excitement = max(0, self.excitement - 1)
            self.happiness = max(0, self.happiness - 1)
            self.last_interaction = now
            self.save_state()

    def mood(self):
        if self.food > 50 and self.excitement > 50:
            return "很開心～"
        elif self.food <= 50:
            return "肚子餓了QQ"
        else:
            return "想要出去玩啦 > <"

    def state(self):
        self.clock_tick()
        return f"我叫 {self.name}，我現在 {self.mood()}."

    def bark(self):
        self.clock_tick()
        barks = ["汪", "汪汪！", "汪汪汪！！", "你知道誰是世界上最可愛的狗狗嗎？是我！汪"]
        return random.choice(barks)

    def teach(self, word):
        self.clock_tick()
        if word:
            self.add_word_to_vocabulary(word)

    def talk(self):
        self.clock_tick()
        vocab = self.read_vocabulary()
        return random.choice(vocab) if vocab else "我現在不會說話"

    def feed(self):
        self.clock_tick()
        self.food = min(100, self.food + random.randint(20, 50))
        self.save_state()
        return "卡茲卡茲～ 好ㄘ好ㄘ" if self.food > 50 else "我不想吃東西"

    def play(self):
        self.clock_tick()
        self.excitement = min(100, self.excitement + random.randint(20, 50))
        self.save_state()
        responses = ['耶依～出門遛遛', '我是快樂ㄉ狗狗！', '我要去聞遍所有的電線杆']
        return random.choice(responses) if self.excitement > 50 else "好無聊喔～帶我出去玩嘛"

    def read_vocabulary(self):
        with self.get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT word FROM vocabularies")
            vocab = [row[0] for row in c.fetchall()]
            # ic(vocab)
        return vocab

    def add_word_to_vocabulary(self, word):
        with self.get_db_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO vocabularies (word, count) VALUES (?, 1)", (word,))
            if c.rowcount == 0:
                c.execute("UPDATE vocabularies SET count = count + 1 WHERE word = ?", (word,))
            conn.commit()

class ChiChi(Pet):
    def __init__(self):
        super().__init__("琪琪", "狗狗")

    def get_vocabularies(self):
        vocabularies = self.read_vocabulary()
        return f"我會說這些詞彙ㄛ！不要教我說髒話\n{ ' '.join(vocabularies) }"

chichi = ChiChi()

