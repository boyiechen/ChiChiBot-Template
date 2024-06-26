import os
import sys
import sqlite3
# Add project folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
static_tmp_path = os.path.join(os.path.dirname(__file__), '../static', 'tmp')

from config import LINE_CHANNEL_ACCESS_TOKEN
from app.services.ChatGPT import Conversation

from linebot.v3.webhooks import (
    MemberJoinedEvent,
    MemberLeftEvent
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)

from config import LINE_CHANNEL_ACCESS_TOKEN
from app.utils.authenticate import add_authorized_user, is_group_authorized, remove_authorized_user


def handle_member_joined(event):
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        for member in event.joined.members:
            if member.type == 'user':
                add_authorized_user(member.user_id, relationship="To be determined")

        group_id = event.source.group_id if event.source.type == 'group' else None
        if group_id:
            if not is_group_authorized(group_id):
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text='This group is not authorized to use this bot.')]
                    )
                )
                return

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text='Welcome new members!')]
            )
        )

def handle_member_left(event):
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    
    # Remove the member from authorized members if leaving
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        for member in event.left.members:
            if member.type == 'user':
                remove_authorized_user(member.user_id)

        group_id = event.source.group_id if event.source.type == 'group' else None
        if group_id:
            if not is_group_authorized(group_id):
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text='This group is not authorized to use this bot.')]
                    )
                )
                return
