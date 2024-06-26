# -*- coding: utf-8 -*-
"""
Main script of ChiChiBot
Author: Boyie Chen
Last Modified: 2024-06-16
"""

import errno
import os
import sys
import time
import datetime
import logging
import tempfile
from argparse import ArgumentParser

# Set the environment variable
os.environ['TZ'] = 'Asia/Taipei'
time.tzset()

# add project folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, abort, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.models import (
    UnknownEvent
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    LocationMessageContent,
    StickerMessageContent,
    ImageMessageContent,
    VideoMessageContent,
    AudioMessageContent,
    FileMessageContent,
    UserSource,
    RoomSource,
    GroupSource,
    FollowEvent,
    UnfollowEvent,
    JoinEvent,
    LeaveEvent,
    PostbackEvent,
    BeaconEvent,
    MemberJoinedEvent,
    MemberLeftEvent,
)
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


# configurations and secrets
from config import *

# 3rd-party libraries
# chatGPT API
import openai
openai.api_key = OPENAI_API_KEY
from app.services.ChatGPT import Conversation

# modulized handlers
from app.handlers.text_message_handler import handle_text_message
from app.handlers.location_message_handler import handle_location_message
from app.handlers.sticker_message_handler import handle_sticker_message
from app.handlers.content_message_handler import handle_content_message
from app.handlers.file_message_handler import handle_file_message
from app.handlers.follow_event_handler import handle_follow, handle_unfollow, handle_join, handle_leave
from app.handlers.postback_event_handler import handle_postback
from app.handlers.beacon_event_handler import handle_beacon
from app.handlers.member_event_handler import handle_member_joined, handle_member_left
from app.handlers.unknown_event_handler import handle_unknown_left

# Load self-defined modules
from app.utils.authenticate import add_authorized_user, add_authorized_group
from app.utils.Scheduler import initialize_schedulers
from app.utils.reminder_scheduler import ReminderScheduler
from app.utils.import_vocabulary import import_vocabularies
# Sticker class
from app.utils.Sticker import sticker


# create Flask app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)

# Configure logging
log_file_path = os.path.join(os.path.dirname(__file__), 'chichibot.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_file_path), logging.StreamHandler()])
app.logger.setLevel(logging.INFO)


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None or channel_access_token is None:
    print('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
    sys.exit(1)

handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

configuration = Configuration(
    access_token=channel_access_token
)


# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except ApiException as e:
        app.logger.warning("Got exception from LINE Messaging API: %s\n" % e.body)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# Add handlers to the webhook handler
handler.add(MessageEvent, message=TextMessageContent)(handle_text_message)
handler.add(MessageEvent, message=LocationMessageContent)(handle_location_message)
# handler.add(MessageEvent, message=StickerMessageContent)(handle_sticker_message)
handler.add(MessageEvent, message=(ImageMessageContent,
                                    VideoMessageContent,
                                    AudioMessageContent))(handle_content_message)
handler.add(MessageEvent, message=FileMessageContent)(handle_file_message)
handler.add(PostbackEvent)(handle_postback)
handler.add(MemberJoinedEvent)(handle_member_joined)
handler.add(MemberLeftEvent)(handle_member_left)


@app.route('/static/<path:path>')
def send_static_content(path):
    return send_from_directory('static', path)


if __name__ == "__main__":

    # run flask in the main thread, and other threads for the scheduler
    if os.environ.get("WERKZEUG_RUN_MAIN") is None:
        # Initialize database
        initialize_db()

        # Every time the server restarts, import authorized users and groups from the environment variables
        for user in AUTHORIZED_USERS:
            add_authorized_user(user['user_id'], user['relationship'])
        for group in AUTHORIZED_GROUPS:
            add_authorized_group(group)

        # import vocabulary
        import_vocabularies('./bot_preconfig/vocabulary.txt', './app/data/chichibot.db')

        # send push message using the scheduler
        schedulers = initialize_schedulers(users=None, groups=AUTHORIZED_GROUPS)
        # Start reminder scheduler
        reminder_scheduler = ReminderScheduler()

    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--host <host>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=3333, help='port')
    arg_parser.add_argument('-d', '--debug', default=True, help='debug')
    arg_parser.add_argument('-H', '--host', default='0.0.0.0', help='host')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()

    app.run(debug=options.debug, host=options.host, port=options.port)
