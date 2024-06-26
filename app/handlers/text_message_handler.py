import os
import sys
import requests
import datetime
import uuid
# Add project folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from icecream import ic

from flask import Flask, request
from linebot.v3.webhooks import MessageEvent, TextMessageContent, UserSource, GroupSource, RoomSource
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

from app.utils.authenticate import is_user_authorized, is_group_authorized
from config import LINE_CHANNEL_ACCESS_TOKEN, CHATBOT_NAME, SQLITE_DB_PATH, IMMICH_API_BASE_URL, IMMICH_API_TOKEN, IMMICH_USER_IDS
from app.services.ChatGPT import Conversation
from app.utils.Tamagotchi import chichi
from app.utils.EventManager import EventManager
from app.handlers.postback_event_handler import recording_sessions
# from app.handlers.content_message_handler import temp_file_paths
from app.services.SimpleImmichAPI import ImmichAPI
from app.utils.clean_up_tmp import clean_up_uploads
from app.services import Immich

immich_client = ImmichAPI(IMMICH_API_BASE_URL, IMMICH_API_TOKEN)
event_manager = EventManager(SQLITE_DB_PATH)

# image carousel sent after "ChiChi Says" command
def send_feedback_image_carousel(response):
    img_url_prefix = request.host_url + os.path.join('static/stickers/')
    image_carousel_template = ImageCarouselTemplate(columns=[
        ImageCarouselColumn(image_url=f"{img_url_prefix}/02.png",
                            action=PostbackAction(label='琪琪可愛', data=f'vocab_good,{response}')),
        ImageCarouselColumn(image_url=f"{img_url_prefix}/01.png",
                            action=PostbackAction(label='笨狗狗', data=f'vocab_neutral,{response}')),
        ImageCarouselColumn(image_url=f"{img_url_prefix}/06.png",
                            action=PostbackAction(label='壞狗狗', data=f'vocab_bad,{response}')),
        ImageCarouselColumn(image_url=f"{img_url_prefix}/04.png",
                            action=PostbackAction(label='玩耍', data='play')),
        ImageCarouselColumn(image_url=f"{img_url_prefix}/08.png",
                            action=PostbackAction(label='餵琪琪', data='feed'))
    ])
    template_message = TemplateMessage(
        alt_text='Feedback buttons', template=image_carousel_template)
    return template_message

# Call Immich API to upload photos and create an album
def prompt_for_album_title(event):
    user_id = event.source.user_id
    recording_sessions[user_id] = {'state': 'album_title', 'group_id': event.source.group_id}
    # ic(recording_sessions)
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text='請輸入相簿名稱，琪琪會幫你建立相簿喔！')]
            )
        )


def create_album_from_session(album_name):

    # Initialize the Immich API
    api_url = f'{IMMICH_API_BASE_URL}/api'
    api_key = IMMICH_API_TOKEN
    Immich.initialize(api_url, api_key)

    # Specify the folder path and album name
    folder_path = './app/data/uploads'
    # ic(os.listdir(folder_path))

    # Fetch existing albums
    albums = Immich.fetchAlbums()

    # Create a new album if it doesn't exist
    album_id = None
    for album in albums:
        if album['albumName'] == album_name:
            album_id = album['id']
            break

    if album_id is None:
        album_id = Immich.createAlbum(album_name)
        if album_id is None:
            print("相簿建立失敗，請琪琪維修師看看QQ")
            exit(1)

    # Upload files and collect asset IDs
    asset_ids = []
    print("Uploading files in the specified folder:")
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                file_path = os.path.join(root, file)
                print(f"Uploading file: {file_path}")
                device_asset_id = str(uuid.uuid4())
                device_id = "device_id_example"
                created_at = datetime.datetime.now().isoformat()
                modified_at = datetime.datetime.now().isoformat()
                asset_id = Immich.upload_file(
                    file_path, device_asset_id, device_id, created_at, modified_at
                )
                if asset_id:
                    asset_ids.append(asset_id)

    # Debug: Print the asset IDs found
    ic(f"Uploaded asset IDs: {asset_ids}")

    Immich.addAssetsToAlbum(album_id, asset_ids)

    ic(f"Added {len(asset_ids)} assets to album {album_name}")

    # finish album creation, clean up temp files
    clean_up_uploads()
    ic("Album creation finished; cleaned up temp files.")

    # Add user to album
    user_ids = IMMICH_USER_IDS  # The user ID to be added as editor
    for user_id in user_ids:
        if Immich.add_user_to_album(album_id, user_id):
            print(f"User {user_id} added to album {album_name} as editor.")

    # Create shared link for the album
    next7days = datetime.datetime.now() + datetime.timedelta(days=7)
    # convert into str
    next7days = next7days.strftime("%Y-%m-%d")
    shared_link = Immich.create_shared_link(album_id, 
                                            asset_ids, 
                                            description="uploaded by ChiChiBot", 
                                            expires_at= next7days,
                                            password=""
                                            )
    # ic(shared_link['key'])
    the_link = f"{IMMICH_API_BASE_URL}/share/{shared_link['key']}"
    # return the shared link
    return(the_link)


def prompt_for_album_confirmation(event, session):
    # user_id = event.source.user_id

    the_shared_link = create_album_from_session(album_name=session['title'])

    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f'相簿建立好了！連結是：\n{the_shared_link}\n琪琪會在七天後吃掉這些相片喔！接下來就到 Immich app 裡看吧～或者是呼叫「琪琪幫幫我」來列出相簿')]
            )
        )


def handle_text_message(event: MessageEvent):
    user_id = event.source.user_id
    group_id = event.source.group_id if event.source.type == 'group' else None
    ic(user_id)
    ic(group_id)
    text = event.message.text
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # Authorization check
        if (not is_user_authorized(user_id)) and (not is_group_authorized(group_id)): # not in authorized users
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='You are not authorized to use this bot. Please add friend to the official account first and then contact the owner with your name. 你並非經過授權的使用者，無法使用此官方帳號。請加入官方帳號好友並且傳送一則訊息給管理員，其中提及你的姓名以便驗證權限')]
                )
            )
            return

        # Log the conversation regardless of "聰明的琪琪"
        chichichat = Conversation(user_id, prompt="", num_of_round=10)
        chichichat.save_recent_message("user", text, group_id)


        # use a dictionary to map Tamagotchi commands to methods
        command, *args = text.split()
        command = command.lower()

        commands = {
            # "profile": get_profile,
            f"{CHATBOT_NAME}": chichi.talk,
            f"{CHATBOT_NAME}叫": chichi.bark,
            f"{CHATBOT_NAME}怎麼了": chichi.state,
            f"{CHATBOT_NAME}說": chichi.talk,
            f"{CHATBOT_NAME}吃": chichi.feed,
            f"{CHATBOT_NAME}玩": chichi.play,
            # f"{CHATBOT_NAME}說": chichi.teach,
            f"{CHATBOT_NAME}會說什麼": chichi.get_vocabularies,
            # f"聰明的{CHATBOT_NAME}": ask_chatgpt
        }

        if command in commands:
            response = commands[command](*args) if args else commands[command]()
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response)]
                )
            )
        elif event.message.text[:3] == f"{CHATBOT_NAME}說":
            chichi.teach(event.message.text[3:])
            message = chichi.talk()
            ic(message)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=chichi.talk()), send_feedback_image_carousel(message)]
                )
            )

        # ChatGPT Integration
        elif text[:(3+len(CHATBOT_NAME))] == f"聰明的{CHATBOT_NAME}":
            chichichat = Conversation(user_id, prompt="", num_of_round=10) 
            chichichat.load_recent_conversation_history(group_id)
            text_to_ask = text[5:]
            message = chichichat.ask(text_to_ask, group_id)  # Now returns a TextMessage with quick reply
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[message]
                )
            )

        # Display help message
        if text == '琪琪幫幫我' or text == "77885":
            buttons_template = ButtonsTemplate(
                title='機器琪琪功能表',
                text='請選擇一項:',
                actions=[
                    PostbackAction(label='建立待辦事項', data='start_recording'),
                    MessageAction(label='列出待辦事項', text='琪琪提醒我'),
                    # MessageAction(label='看琪琪', text='琪琪怎麼了'),
                    # MessageAction(label='餵琪琪', text='琪琪吃'),
                    # MessageAction(label='逗琪琪', text='琪琪叫'),
                    # MessageAction(label='跟琪琪玩', text='琪琪玩'),
                    # MessageAction(label='教琪琪說話', text='琪琪說'),
                    MessageAction(label='琪琪找相簿', text='相簿'),
                    MessageAction(label='跟聰明的琪琪說話', text='聰明的琪琪告訴我誰是世界上最聰明的笨狗狗?')
                ])
            template_message = TemplateMessage(
                alt_text='Help buttons', template=buttons_template)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )

        # Event Reminder
        elif text == '琪琪提醒我':
            events = event_manager.get_upcoming_events(user_id, group_id)
            ic("current events", events)
            if len(events) == 0:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text='目前沒有待辦事項喔！')]
                    )
                )
                return
            columns = [
                CarouselColumn(
                    text=event[2],
                    title=event[1],
                    actions=[
                        PostbackAction(label='Delete', data=f'event_delete,{event[0]}')
                    ]
                ) for event in events
            ]
            carousel_template = CarouselTemplate(columns=columns)
            template_message = TemplateMessage(
                alt_text='Event List', template=carousel_template)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        # When the user creates the event, a title needs to be recorded
        if user_id in recording_sessions:
            session = recording_sessions[user_id]
            if session['state'] == 'title_recording':
                # Save the title and move to description recording
                session['title'] = text
                session['state'] = 'description_recording'

                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text='請輸入待辦事項的描述')]
                    )
                )
            elif session['state'] == 'description_recording':
                # Save the description and prompt for due date or datetime
                session['description'] = text
                session['state'] = 'due_date_confirmation'

                quick_reply = QuickReply(
                    items=[
                        QuickReplyItem(action=PostbackAction(label="加入日期", data="add_due_date")),
                        QuickReplyItem(action=PostbackAction(label="加入日期和時間", data="add_due_datetime")),
                        QuickReplyItem(action=PostbackAction(label="不加入", data="no_due_date"))
                    ]
                )

                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text='請選擇是否加入截止日期或截止時間', quick_reply=quick_reply)]
                    )
                )
            
            # case: the recording session is associated with photo album creation
            elif session['state'] == 'album_title':
                album_title = text
                session['title'] = album_title
                session['state'] = 'confirm_creation'
                prompt_for_album_confirmation(event, session)


        # Immich Service
        if text.lower() == "create album":
            prompt_for_album_title(event)
        elif text.lower() == "discard photos":
            clean_up_uploads()
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token = event.reply_token, 
                    messages = [TextMessage(text="琪琪把相片吃掉惹")]
                )
            )

        elif text == 'carousel':
            carousel_template = CarouselTemplate(
                columns=[
                    CarouselColumn(
                        text='hoge1',
                        title='fuga1',
                        actions=[
                            URIAction(label='Go to line.me', uri='https://line.me'),
                            PostbackAction(label='ping', data='ping')
                        ]
                    ),
                    CarouselColumn(
                        text='hoge2',
                        title='fuga2',
                        actions=[
                            PostbackAction(label='ping with text', data='ping', text='ping'),
                            MessageAction(label='Translate Rice', text='米')
                        ]
                    )
                ]
            )
            template_message = TemplateMessage(
                alt_text='Carousel alt text', template=carousel_template)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )

        elif text.lower() == "相簿":
            # Initialize the Immich API
            api_url = f'{IMMICH_API_BASE_URL}/api'
            api_key = IMMICH_API_TOKEN
            Immich.initialize(api_url, api_key)
            
            # Fetch all albums and convert to DataFrame
            albums = immich_client.get_albums()
            df_albums = immich_client.convert_json_album_todataframe(albums)
            
            # Shuffle and select 5 random albums
            df_albums = df_albums.sample(frac=1).reset_index(drop=True)
            selected_albums = df_albums.head(8)
            
            # Initialize shared links list, it will store a 5-item tuple of (album_name, shared_link, thumbnail_id, thumbnail_link, thumbnail_disk_link)
            shared_links = []
            # set expiration date
            next7days = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            
            for _, album in selected_albums.iterrows():
                album_id = album['id']
                asset_ids = [asset['id'] for asset in album['assets']]
                
                # Check if shared link already exists
                shared_link = Immich.create_shared_link(album_id, asset_ids, description="uploaded by ChiChiBot", expires_at=next7days, password="")
                if shared_link:
                    # get the full shared link using the `key` from the response
                    shared_link_url = f"https://immich.angelchichi.com/share/{shared_link['key']}"
                    # if album has a thumbnail, download it and use it in the image carousel
                    if album['albumThumbnailAssetId'] is not None:
                        shared_links.append((album['albumName'], 
                                            shared_link_url, 
                                            album['albumThumbnailAssetId'],
                                            f"https://immich.angelchichi.com/api/asset/thumbnail/{album['albumThumbnailAssetId']}?format=JPEG",
                                            f"{request.host_url + os.path.join('static/album_thumbnails', album['albumThumbnailAssetId'])}.jpg"
                                            ))
            # ic(shared_links)

            # download the thumbnails into tmp folder first
            # and then use the host + static path in the image carousel
            for name, link, thumbnail_id, thumbnail_link, thumbial_disk_link in shared_links:
                r = requests.get(thumbnail_link, headers={'x-api-key': IMMICH_API_TOKEN, 'Accept': 'application/json'})
                dist_path = f"./app/static/album_thumbnails/{thumbnail_id}.jpg"
                with open(dist_path, 'wb') as f:
                    f.write(r.content)
            
            # Create image carousel
            image_carousel_columns = [
                ImageCarouselColumn(
                    image_url=thumbnail_disk_link,
                    action=URIAction(label=name[0:11], uri=f'{link}'),
                )
                for name, link, thumbnail_id, thumbnail_link, thumbnail_disk_link in shared_links
            ]
            image_carousel_template = ImageCarouselTemplate(columns=image_carousel_columns)
            template_message = TemplateMessage(
                alt_text='ImageCarousel alt text', template=image_carousel_template)
            
            # send the image carousel
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token = event.reply_token, 
                    messages = [TextMessage(text=f"琪琪亂翻出了{len(shared_links)}本相簿！汪！"), template_message]
                )
            )
