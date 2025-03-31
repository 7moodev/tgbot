from invoke import task

@task
def wallet(ctx):
    ctx.run('python -m backend.commands.utils.wallet_utils')
@task
def token(ctx):
    ctx.run('python -m backend.commands.utils.token_utils')
@task
def general(ctx):
    ctx.run('python -m backend.commands.utils.general_utils')
@task
def fresh(ctx):
    ctx.run('python -m backend.commands.fresh_wallets')
@task
def freshv2(ctx):
    ctx.run('python -m backend.commands.fresh_wallets_v2')

@task
def avg(ctx):
    ctx.run('python -m backend.commands.holders_avg_entry_price')

@task
def disto(ctx):
    ctx.run('python -m backend.commands.holding_distribution')

@task
def noteworthy(ctx):
    ctx.run('python -m backend.commands.noteworthy_addresses')
@task
def top(ctx):
    ctx.run('python -m backend.commands.top_holders_holdings')

@task
def parser(ctx):
    ctx.run('python -m backend.bot.parser')



@task
def main2(ctx):
    ctx.run('python -m backend.bot.main2')

@task 
def payment(ctx):
    ctx.run('python -m backend.bot.paywall.payment')

@task
def user_log(ctx):
    ctx.run('python -m db.user.log')

@task
def main(ctx):
    ctx.run('python -m backend.bot.main')

@task
def api(ctx):
    ctx.run('uvicorn backend.api.main:app --reload')