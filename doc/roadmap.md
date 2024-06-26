# Road map and planned features

- [ ] integrate with LLM and memory
  - [ ] able to streamline with Ollama local models
  - [x] able to memorize past conversations
  - [x] RAG powered dialogues (read contextualized texts)
- [x] LineBot authentication
  - [x] able to know which user is talking
  - [x] able to know which group chat the bot is in -- only authorized group can use
  - [x] link user identification with specific chat history

- [ ] Misc features
  - [ ] able to read images (can be done with Azure API, but how to do that more privately?)
  - [ ] able to reply in short audio (generate audio from text)
  - [ ] able to reply with images (image generation)
  - [x] able to gain feedbacks from users (perhaps integrate with flex response after each round)
  - [ ] Immich API to upload photos (considering replace current Google Photo API)
  - [x] able to remind upcoming events (before 1 month, before 1 week, before 1 day)
  - [ ] Simple tamagotchi game play
    - [x] being able to actively send messages in different status
      - [x] being hungry, being bored, ... etc. No more than one message per day to avoid bothering the group.
      - [ ] interact with users (using flex message) to change the status
  
- [ ] Sanity check
  - [ ] log the requests
  - [x] log the latest 100 messages -- on a rolling basis
  - [x] use env variables to load the DB's path
  - [ ] auto create the `db_backup` folder if not exist

- Feature requests
  - [x] calendar reminder
  - [ ] water reminder (pop up a flex message to fill up the water bottle) 為了讓琪琪踢不動這個空碗，也為了身體健康，加把勁多喝點水吧！