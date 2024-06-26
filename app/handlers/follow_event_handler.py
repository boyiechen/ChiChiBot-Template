import os
import sys
import datetime
import tempfile
# Add project folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
static_tmp_path = os.path.join(os.path.dirname(__file__), '../static', 'tmp')

from flask import Flask, request
from linebot.v3.webhooks import MessageEvent, TextMessageContent, UserSource, GroupSource, RoomSource, ImageMessageContent, VideoMessageContent, AudioMessageContent
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    PushMessageRequest,
    MulticastRequest,
    BroadcastRequest,
    TextMessage,
    ApiException,
    LocationMessage,
    StickerMessage,
    ImageMessage,
    TemplateMessage,
    FlexMessage,
    Emoji,
    QuickReply,
    QuickReplyItem,
    ConfirmTemplate,
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    FlexBubble,
    FlexImage,
    FlexBox,
    FlexText,
    FlexIcon,
    FlexButton,
    FlexSeparator,
    FlexContainer,
    MessageAction,
    URIAction,
    PostbackAction,
    DatetimePickerAction,
    CameraAction,
    CameraRollAction,
    LocationAction,
    ErrorResponse
)
from linebot.v3.insight import (
    ApiClient as InsightClient,
    Insight
)

from config import LINE_CHANNEL_ACCESS_TOKEN
from app.services.ChatGPT import Conversation

def handle_follow(event):
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    # app.logger.info("Got Follow event:" + event.source.user_id)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text='Got follow event')]
            )
        )

def handle_unfollow(event):
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    # app.logger.info("Got Unfollow event:" + event.source.user_id)

def handle_join(event):
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text='Joined this ' + event.source.type)]
            )
        )

def handle_leave():
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    # app.logger.info("Got leave event")