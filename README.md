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
python -m backend.bot.main2

### Useful
- check if your bot is running
  - https://api.telegram.org/bot<token>/getMe

#### Logs
- Heroku
  - heroku logs --tail -a munki-tg-bot
  - heroku logs --num 1500 -a munki-tg-bot
  - git push heroku main
  - heroku ps:scale web=n -app $APP_NAME

#### Package Management
- freeze requirements.txt after installing a package
  - pip freeze > requirements.txt

### Testing
- pytest
  - https://docs.pytest.org/en/stable/getting-started.html
  - only run this test(s)
    - pytest -k only
      - and decorate your test with `@pytest.mark.only`
- coverage
  - coverage run -m pytest arg1 arg2 arg3
  - coverage report
  - coverage html
  - coverage html && open htmlcov/index.html
  - coverage run -m pytest -k only
- tox
  - https://tox.wiki/en/4.24.1/
  - https://pypi.org/project/tox/

#### Example
cd /tests/examples
- pytest
- pytest -q test_sysexit.py
