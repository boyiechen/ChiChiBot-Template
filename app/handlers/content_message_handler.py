# app/handlers/content_message_handler.py

import os
import sys
import tempfile
import threading
from icecream import ic
# Add project folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
static_tmp_path = os.path.join(os.path.dirname(__file__), '../data', 'uploads')
from flask import request
from linebot.v3.webhooks import MessageEvent, ImageMessageContent, VideoMessageContent, AudioMessageContent
from linebot.v3.messaging import (
    Configuration, 
    ApiClient, 
    MessagingApi, 
    MessagingApiBlob,
    ReplyMessageRequest, 
    TextMessage, 
    QuickReply, 
    QuickReplyItem, 
    MessageAction,
)
from config import LINE_CHANNEL_ACCESS_TOKEN, IMMICH_API_BASE_URL, IMMICH_API_TOKEN
from app.services.SimpleImmichAPI import ImmichAPI

immich_api = ImmichAPI(IMMICH_API_BASE_URL, IMMICH_API_TOKEN)

def handle_content_message(event):
    user_id = event.source.user_id
    ic(user_id)
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    if isinstance(event.message, ImageMessageContent):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessageContent):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessageContent):
        ext = 'm4a'
    else:
        return

    with ApiClient(configuration) as api_client:
        line_bot_blob_api = MessagingApiBlob(api_client)
        message_content = line_bot_blob_api.get_message_content(message_id=event.message.id)

        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
            tf.write(message_content)
            tempfile_path = tf.name
            ic(tempfile_path)

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)
    ic(dist_path)
    ic(dist_name)
    save_temp_file_path(event.source.user_id, dist_path)
    ic(temp_file_paths)

    # Start a timer to send the quick reply message after a short delay
    if user_id not in timers:
        timers[user_id] = threading.Timer(8.0, send_quick_reply_message, args=[event.reply_token, user_id])
        timers[user_id].start()

def save_temp_file_path(user_id, file_path):
    if user_id not in temp_file_paths:
        temp_file_paths[user_id] = []
    temp_file_paths[user_id].append(file_path)

def send_quick_reply_message(reply_token, user_id):
    quick_reply = QuickReply(items=[
        QuickReplyItem(action=MessageAction(label="幫我建立相簿", text="Create Album")),
        QuickReplyItem(action=MessageAction(label="不要", text="Discard Photos"))
    ])

    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text='琪琪刁著照片問你，請問你讓琪琪建立相簿嗎？', quick_reply=quick_reply)]
            )
        )
    
    # Remove the timer entry after sending the message
    if user_id in timers:
        del timers[user_id]

temp_file_paths = {}
timers = {}
