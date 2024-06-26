import os
import threading
import json
import sqlite3
import shutil
import time
import logging
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

# Project Path
PROJECT_PATH = os.getenv("PROJECT_PATH")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLite Database
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH")

# Line-bot channel
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# Load authorized users and groups from JSON file
with open('./bot_preconfig/authorized_users.json', 'r') as f:
    auth_data = json.load(f)
    AUTHORIZED_USERS = auth_data['authorized_users']
    AUTHORIZED_GROUPS = auth_data['authorized_groups']

# Exchange rate API
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
EXCHANGE_RATE_ENDPOINT = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/USD"

#
IMMICH_API_BASE_URL = os.getenv("IMMICH_API_BASE_URL")
IMMICH_API_TOKEN = os.getenv("IMMICH_API_TOKEN")
IMMICH_USER_IDS = os.getenv("IMMICH_USER_IDS").split(',')

# Google photo api
GPHOTO_CLIENT_ID = os.getenv("GPHOTO_CLIENT_ID")
GPHOTO_CLIENT_SECRET = os.getenv("GPHOTO_CLIENT_SECRET")

# Imgur
IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")
IMGUR_CLIENT_SECRET = os.getenv("IMGUR_CLIENT_SECRET")

# Azure
AZURE_COMPUTER_VISION_KEY = os.getenv("AZURE_COMPUTER_VISION_KEY")
AZURE_COMPUTER_VISION_ENDPOINT = os.getenv("AZURE_COMPUTER_VISION_ENDPOINT")

# OpenAI API KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ChatBot Characteristics
CHATBOT_NAME = os.getenv("CHATBOT_NAME")
CHATBOT_SPECIES = os.getenv("CHATBOT_SPECIES")
CHATBOT_ROLE_DESCRIPTION = os.getenv("CHATBOT_ROLE_DESCRIPTION")

# Initializing folder structure
if not os.path.exists('app/data/uploads'):
    os.mkdir('app/data/uploads')

# To store the database backup
if not os.path.exists('app/data/db_backup'):
    os.mkdir('app/data/db_backup')

# To store the album thumbnails
if not os.path.exists('app/static/album_thumbnails'):
    os.mkdir('app/static/album_thumbnails')

# Flag to check if initialization is done
INITIALIZED = False

# Define the desired schema
DESIRED_SCHEMA = {
    'conversations': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'user_id TEXT NOT NULL',
        'role TEXT NOT NULL',
        'content TEXT NOT NULL',
        'context TEXT',
        'score INTEGER',
        'timestamp DATETIME DEFAULT CURRENT_TIMESTAMP'
    ],
    'authorized_groups': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'group_id TEXT NOT NULL UNIQUE'
    ],
    'authorized_users': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'user_id TEXT NOT NULL UNIQUE',
        'relationship TEXT NOT NULL'
    ],
    'recent_conversations': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'user_id TEXT NOT NULL',
        'role TEXT NOT NULL',
        'content TEXT NOT NULL',
        'group_id TEXT',
        'timestamp DATETIME DEFAULT CURRENT_TIMESTAMP'
    ],
    'tamagotchi': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'name TEXT NOT NULL',
        'animal_type TEXT NOT NULL',
        'food INTEGER NOT NULL',
        'excitement INTEGER NOT NULL',
        'happiness INTEGER NOT NULL',
        'last_interaction DATETIME NOT NULL'
    ],
    'vocabularies': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'word TEXT NOT NULL UNIQUE',
        'count INTEGER NOT NULL DEFAULT 1',
        'human_weight INTEGER NOT NULL DEFAULT 0'
    ],
    'events': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'title TEXT NOT NULL',
        'description TEXT NOT NULL',
        'event_date DATETIME NOT NULL',
        'location TEXT NOT NULL',
        'group_id TEXT',
        'user_ids TEXT NOT NULL'
    ],
}

def get_current_schema(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema = {}
    for table_name in tables:
        table_name = table_name[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        schema[table_name] = [f"{column[1]} {column[2]}" for column in columns]

    return schema

# Initialization lock
initialization_lock = threading.Lock()

# Function for initializing the database
def initialize_db():
    global INITIALIZED
    with initialization_lock:
        if INITIALIZED:
            logger.info("Database already initialized.")
            return

        logger.info("Initializing database...")

        if os.path.exists(SQLITE_DB_PATH):
            conn = sqlite3.connect(SQLITE_DB_PATH)
            current_schema = get_current_schema(conn)
            conn.close()

            if current_schema != DESIRED_SCHEMA:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                backup_db_path = f"{PROJECT_PATH}/app/data/db_backup/backup_{timestamp}.db"
                shutil.move(SQLITE_DB_PATH, backup_db_path)
                logger.info(f"Existing database schema does not match. Renamed to {backup_db_path}")

        conn = sqlite3.connect(SQLITE_DB_PATH)
        c = conn.cursor()

        # Create tables with the desired schema
        for table, columns in DESIRED_SCHEMA.items():
            columns_str = ', '.join(columns)
            c.execute(f"CREATE TABLE IF NOT EXISTS {table} ({columns_str})")

        conn.commit()
        conn.close()

        INITIALIZED = True
        logger.info("Database initialization completed.")


if __name__ == "__main__":
    # Initialize the database
    initialize_db()

    # Load authorized users and groups from JSON file
    with open('./bot_preconfig/authorized_users.json', 'r') as f:
        auth_data = json.load(f)
        AUTHORIZED_USERS = auth_data['authorized_users']
        AUTHORIZED_GROUPS = auth_data['authorized_groups']

    print(AUTHORIZED_USERS)
