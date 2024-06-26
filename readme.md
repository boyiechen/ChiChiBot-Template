# Description

ChiChiBot is a linebot for family usage in a line group chat. 
An user can build her own line chatbot using this template and deploy it on her own server.

# Main Feathures

- Chat
  - empowered by LLM such as chatGPT, the chatbot can chat with the user and provide emotional support for elder family members.
  - Simply set up the bot characteristics just like role playing, the bot can behave like a real family member in the group chat.
  - For example, ChiChi is my dog's name, though she has passed away for years, I set up the bot to behave like her and continue her accompany with my family in the family group chat.

- Tamagotchi
  - Text message interaction with the tamagotchi
  - Feed the dog, play with the dog, and check the status of the dog

- Integration of Immich service 
  - Using Immich as a self-host image hosting service, the bot can upload images and create albums for the user.
  - Easily manage family albums in a secure and private way.
  - Browse the albums and the past event photos in the group chat by interacting with the bot.

- Misc Features
  - Sticker sending
  - Exchange rate query
  - Reminder setting and notification
  - Temporary file uploading and downloading via thee deployed server


# Deployment

To deploy the project, make sure the environment and the configuration are set up correctly.

## Environment

- See `runtime.txt` for the python version
- See `requirements.txt` for the python packages
- See `.env.template` for the environment variables
- See `config.py` for the configuration
- Set up `bot_preconfig`:
  - `authorized_users.json.template` for the authorized users. See Line's Messaging API documentation for more information.
  - (Optional) `vocabulary.txt` is the dictionary of vocabulary that the chatbot know prior to any conversation. 

## Other Dependencies

### Immich Service
The user may need to have her own Immich instance and create an API key to integrate the chatbot with the service. 


# Project Structure

```bash
.
├── app
│   ├── __init__.py
│   ├── data
│   │   ├── chichibot.db
│   │   └── uploads
│   ├── handlers
│   │   ├── beacon_event_handler.py
│   │   ├── content_message_handler.py
│   │   ├── file_message_handler.py
│   │   ├── follow_event_handler.py
│   │   ├── location_message_handler.py
│   │   ├── member_event_handler.py
│   │   ├── postback_event_handler.py
│   │   ├── sticker_message_handler.py
│   │   ├── text_message_handler.py
│   │   └── unknown_event_handler.py
│   ├── main.py
│   ├── models
│   ├── services
│   │   ├── ChatGPT.py
│   │   ├── Immich.py
│   │   ├── SimpleImmichAPI.py
│   │   └── testImmich.py
│   ├── static
│   │   ├── font
│   │   │   └── NotoSansTC-Regular.otf
│   │   ├── stickers
│   │   │   ├── 01.png
│   │   │   ├── 02.png
│   │   │   ├── 03.png
│   │   │   ├── 04.png
│   │   │   ├── 05.png
│   │   │   ├── 06.png
│   │   │   ├── 07.png
│   │   │   ├── 08.png
│   │   │   ├── 09.png
│   │   │   ├── 10.png
│   │   │   ├── 11.png
│   │   │   ├── 12.png
│   │   │   ├── 13.png
│   │   │   ├── 14.png
│   │   │   ├── 15.png
│   │   │   ├── 16.png
│   │   │   ├── ChiChiCute.png
│   │   │   ├── main.png
│   │   │   ├── stickerSent.png
│   │   │   └── tab.png
│   │   └── tmp
│   └── utils
│       ├── EventManager.py
│       ├── ExchangeRate.py
│       ├── Scheduler.py
│       ├── Sticker.py
│       ├── Tamagotchi.py
│       ├── authenticate.py
│       ├── clean_up_tmp.py
│       ├── import_vocabulary.py
│       └── reminder_scheduler.py
├── bot_preconfig
│   ├── authorized_users.json.template
│   └── vocabulary.txt
├── config.py
├── doc
│   └── roadmap.md
├── readme.md
├── reference
│   ├── flask-kitchensink
│   │   ├── app.py
│   │   ├── readme.md
│   │   ├── requirements.txt
│   │   └── static
│   │       └── Line Bot SDK Logo.png
│   └── templates
│       └── Tamagotchi_template.py
├── requirements.txt
└── runtime.txt
```


# Run the project

```shell
cd PROJECT_REPO
export PYTHONPATH=$(pwd)
python app/main.py
```
