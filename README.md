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
- freeze requirements.txt after installing a package
  - pip freeze > requirements.txt

### Testing
- pytest
    - https://docs.pytest.org/en/stable/getting-started.html
- coverage
  - coverage run -m pytest arg1 arg2 arg3
  - coverage report
  - coverage html
  - coverage html && open htmlcov/index.html
- tox
  - https://tox.wiki/en/4.24.1/
  - https://pypi.org/project/tox/

#### Example
cd /tests/examples
- pytest
- pytest -q test_sysexit.py
