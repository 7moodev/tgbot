# tgbot
are you gonna make it finally, anon?

## Development

### Installation

#### Linux
- Install Postgres
  sudo apt-get install libpq-dev

- Create .env in the root
  source .env

### Run
python backend/bot/main2.py

### Useful
- check if your bot is running
  - https://api.telegram.org/bot<token>/getMe
- Heroku
  - heroku logs --tail -a munki-tg-bot
  - heroku logs --num 1500 -a munki-tg-bot


### Testing
- pytest
    - https://docs.pytest.org/en/stable/getting-started.html
- tox
  - https://tox.wiki/en/4.24.1/
  - https://pypi.org/project/tox/
