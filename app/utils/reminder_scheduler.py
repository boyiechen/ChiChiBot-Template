import threading
import time
from datetime import datetime, timedelta
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, PushMessageRequest, TextMessage
from config import LINE_CHANNEL_ACCESS_TOKEN, SQLITE_DB_PATH
import sqlite3
from icecream import ic

class ReminderScheduler:
    def __init__(self):
        self.configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
        self.api_client = ApiClient(self.configuration)
        self.line_bot_api = MessagingApi(self.api_client)
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def get_db_connection(self):
        return sqlite3.connect(SQLITE_DB_PATH)

    def check_reminders(self):
        with self.get_db_connection() as conn:
            c = conn.cursor()
            now = datetime.now()
            reminders = [
                (7, '一個禮拜'),
                (3, '三天'),
                (1, '一天')
            ]
            for days, label in reminders:
                check_date = (now + timedelta(days=days)).strftime("%Y-%m-%d")
                ic(check_date)
                c.execute('''
                    SELECT id, title, description, event_date, location, group_id, user_ids
                    FROM events
                    WHERE DATE(event_date) = ?
                ''', (check_date,))
                events = c.fetchall()
                for event in events:
                    ic(event)
                    self.send_reminder(event, label)

    def send_reminder(self, event, label):
        event_id, title, description, event_date, location, group_id, user_ids = event
        user_ids = user_ids.split(',')
        message_text = f'提醒：您的待辦事項 "{title}" 還有 {label} 到期！'
        for user_id in user_ids:
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=user_id,
                    messages=[TextMessage(text=message_text)]
                )
            )
        if group_id:
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=group_id,
                    messages=[TextMessage(text=message_text)]
                )
            )

    def run(self):
        while True:
            self.check_reminders()
            time.sleep(86400)  # Check once a day
            ic("ReminderScheduler running...")

