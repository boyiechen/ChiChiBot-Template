import threading
import time
from datetime import datetime, timedelta
import random
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, PushMessageRequest, TextMessage
from config import LINE_CHANNEL_ACCESS_TOKEN
from app.utils.Tamagotchi import chichi

class ChiChiBotScheduler:
    def __init__(self, user_id=None, group_id=None):
        self.user_id = user_id
        self.group_id = group_id
        self.configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
        self.api_client = ApiClient(self.configuration)
        self.line_bot_api = MessagingApi(self.api_client)
        self.sent_times = []
        self.schedule_times = self.generate_random_times()
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def generate_random_times(self):
        times = []
        start_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        end_time = datetime.now().replace(hour=22, minute=0, second=0, microsecond=0)
        delta = (end_time - start_time).total_seconds()
        
        while len(times) < 2:
            rand_seconds = random.randint(0, int(delta))
            random_time = start_time + timedelta(seconds=rand_seconds)
            if len(times) == 0 or (random_time - times[0]).total_seconds() > 10800:  # 3 hours in seconds
                times.append(random_time)
        return sorted(times)

    def run(self):
        while True:
            now = datetime.now()
            if len(self.sent_times) < 2 and now >= self.schedule_times[len(self.sent_times)]:
                self.send_message(chichi.state())
                self.sent_times.append(now)
            if len(self.sent_times) >= 2 or now.hour >= 22:
                # Calculate time to sleep until the next reset
                next_reset = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                time.sleep((next_reset - datetime.now()).total_seconds())
                self.sent_times = []
                self.schedule_times = self.generate_random_times()
            time.sleep(60)  # Check every minute

    def send_message(self, message):
        if self.user_id:
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=self.user_id,
                    messages=[TextMessage(text=message)]
                )
            )
        elif self.group_id:
            self.line_bot_api.push_message(
                PushMessageRequest(
                    to=self.group_id,
                    messages=[TextMessage(text=message)]
                )
            )

# Initialize the scheduler for each user and group
def initialize_schedulers(users=None, groups=None):
    if users is None:
        users = []
    if groups is None:
        groups = []

    schedulers = []
    for user in users:
        schedulers.append(ChiChiBotScheduler(user_id=user['user_id']))
    for group in groups:
        schedulers.append(ChiChiBotScheduler(group_id=group))
    return schedulers

