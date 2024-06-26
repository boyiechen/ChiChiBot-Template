import os
import sys
import datetime
import tempfile
import sqlite3
from icecream import ic
# Add project folder to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
static_tmp_path = os.path.join(os.path.dirname(__file__), '../static', 'tmp')

from linebot.v3.webhooks import PostbackEvent

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    TemplateMessage,
    ButtonsTemplate,
    PostbackAction,
    CarouselTemplate,
    CarouselColumn,
    DatetimePickerAction
)

from config import LINE_CHANNEL_ACCESS_TOKEN, CHATBOT_NAME, SQLITE_DB_PATH
from app.services.ChatGPT import update_score
from app.utils.Tamagotchi import chichi
from app.utils.EventManager import EventManager

event_manager = EventManager(SQLITE_DB_PATH)
recording_sessions = {}

def handle_chatgpt_feedback(reply_id, feedback):
    if feedback == 'good':
        score = 1
        text_reply = '主人也很棒～汪汪！'
    elif feedback == 'neutral':
        score = 0
        text_reply = f'聰明的{CHATBOT_NAME}覺得主人在敷衍她，但她還是會繼續努力～汪！'
    elif feedback == 'bad':
        score = -1
        text_reply = f'聰明的{CHATBOT_NAME}收到主人的回饋了，下次一定會做得更好～嗚汪！'
    else:
        score = None
        text_reply = ''

    if score is not None:
        update_score(reply_id, score)
    return text_reply

def handle_vocab_feedback(word, feedback):
    if feedback == 'good':
        weight_adjustment = 1
        text_reply = '琪琪記住了！'
    elif feedback == 'neutral':
        weight_adjustment = 0
        text_reply = '琪琪會繼續努力記住的～'
    elif feedback == 'bad':
        weight_adjustment = -1
        text_reply = '琪琪會努力不說壞話的～'
    else:
        weight_adjustment = None
        text_reply = ""

    if weight_adjustment is not None:
        update_vocabulary_weight(word, weight_adjustment)
    return text_reply

def handle_event_feedback(event_id, feedback):
    if feedback == 'delete':
        event_manager.delete_event(event_id)
        text_reply = '琪琪把待辦事項吃掉了！口卡口卡'
    else:
        text_reply = ''
    return text_reply

def handle_play():
    return chichi.play()

def handle_feed():
    return chichi.feed()

def handle_start_recording(user_id, group_id, event=None):
    recording_sessions[user_id] = {'state': 'title_recording', 'group_id': group_id}

    cancel_button = ButtonsTemplate(
        title='琪琪正在等待你的指令...',
        text='在對話框輸入待辦事項標題，送出後琪琪就會筆記下來',
        actions=[PostbackAction(label='取消動作', data='cancel_recording')]
    )
    template_message = TemplateMessage(
        alt_text='Recording action', template=cancel_button
    )
    return template_message

def handle_cancel_recording(user_id):
    if user_id in recording_sessions:
        del recording_sessions[user_id]
    return '琪琪不寫筆記了'

def update_vocabulary_weight(word, weight_adjustment):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE vocabularies SET human_weight = human_weight + ? WHERE word = ?", (weight_adjustment, word))
    conn.commit()
    conn.close()

def handle_postback(event: PostbackEvent):
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    
    data = event.postback.data.split(',')
    action = data[0]
    if len(data) > 1:
        identifier = data[1]  # This could be reply_id or word depending on the prefix
    else:
        identifier = None

    if action.startswith('chatgpt_'):
        feedback = action[len('chatgpt_'):]
        text_reply = handle_chatgpt_feedback(int(identifier), feedback)

    elif action.startswith('vocab_'):
        feedback = action[len('vocab_'):]
        text_reply = handle_vocab_feedback(identifier, feedback)
    
    elif action.startswith('event_'):
        feedback = action[len('event_'):]
        text_reply = handle_event_feedback(int(identifier), feedback)
    
    elif action == 'play':
        text_reply = handle_play()
    
    elif action == 'feed':
        text_reply = handle_feed()

    elif action == 'start_recording':
        if event.source.type == 'user':
            text_reply = handle_start_recording(event.source.user_id, None)
        elif event.source.type == 'group':
            text_reply = handle_start_recording(event.source.user_id, event.source.group_id)
        else:
            text_reply = '只有在私訊或群組裡才能使用這個功能唷～'

    elif action == 'cancel_recording':
        text_reply = handle_cancel_recording(event.source.user_id)
    
    elif action == 'add_due_date':
        recording_sessions[event.source.user_id]['state'] = 'due_date'
        date_picker = TemplateMessage(
            alt_text='Date Picker',
            template=ButtonsTemplate(
                title='選擇截止日期',
                text='請選擇截止日期：',
                actions=[DatetimePickerAction(label='選擇日期', data='date_postback', mode='date')]
            )
        )
        text_reply = date_picker

    elif action == 'add_due_datetime':
        recording_sessions[event.source.user_id]['state'] = 'due_datetime'
        datetime_picker = TemplateMessage(
            alt_text='Datetime Picker',
            template=ButtonsTemplate(
                title='選擇截止日期和時間',
                text='請選擇截止日期和時間：',
                actions=[DatetimePickerAction(label='選擇日期和時間', data='datetime_postback', mode='datetime')]
            )
        )
        text_reply = datetime_picker

    elif action == 'no_due_date':
        user_id = event.source.user_id
        session = recording_sessions[user_id]
        event_title = session.get('title', '無標題')
        event_description = session.get('description', '無描述')
        event_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        location = "Sample Location"
        group_id = session['group_id']
        user_ids = [user_id]
        event_manager.create_event(event_title, event_description, event_date, location, group_id, user_ids)
        del recording_sessions[user_id]

        events = event_manager.get_upcoming_events(user_id, group_id)
        columns = [
            CarouselColumn(
                text=event[2],
                title=event[1],
                actions=[
                    PostbackAction(label='刪除待辦事項', data=f'event_delete,{event[0]}')
                ]
            ) for event in events
        ]
        carousel_template = CarouselTemplate(columns=columns)
        template_message = TemplateMessage(
            alt_text='Event List', template=carousel_template)
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='琪琪幫你建立待辦清單了！'), template_message]
                )
            )
        return

    elif action == 'datetime_postback' or action == 'date_postback':
        user_id = event.source.user_id
        session = recording_sessions[user_id]
        event_title = session.get('title', '無標題')
        event_description = session.get('description', '無描述')
        event_date = event.postback.params['datetime'] if action == 'datetime_postback' else event.postback.params['date']
        location = "Sample Location"
        group_id = session['group_id']
        user_ids = [user_id]
        event_manager.create_event(event_title, event_description, event_date, location, group_id, user_ids)
        del recording_sessions[user_id]

        events = event_manager.get_upcoming_events(user_id, group_id)
        columns = [
            CarouselColumn(
                text=event[2],
                title=event[1],
                actions=[
                    PostbackAction(label='刪除待辦事項', data=f'event_delete,{event[0]}')
                ]
            ) for event in events
        ]
        carousel_template = CarouselTemplate(columns=columns)
        template_message = TemplateMessage(
            alt_text='Event List', template=carousel_template)
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='琪琪幫你建立待辦清單了！'), template_message]
                )
            )
        return

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if isinstance(text_reply, TemplateMessage):
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[text_reply]
                )
            )
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=text_reply)]
                )
            )

