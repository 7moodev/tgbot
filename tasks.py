from invoke import task

@task
def wallet(ctx):
    ctx.run('/usr/local/bin/python3.11 -m backend.commands.utils.wallet_utils')
@task
def token(ctx):
    ctx.run('/usr/local/bin/python3.11 -m backend.commands.utils.token_utils')
@task
def general(ctx):
    ctx.run('/usr/local/bin/python3.11 -m backend.commands.utils.general_utils')
@task
def fresh(ctx):
    ctx.run('/usr/local/bin/python3.11 -m backend.commands.fresh_wallets')
@task
def freshv2(ctx):
    ctx.run('/usr/local/bin/python3.11 -m backend.commands.fresh_wallets_v2')

@task
def avg(ctx):
    ctx.run('/usr/local/bin/python3.11 -m backend.commands.holders_avg_entry_price')

@task
def disto(ctx):
    ctx.run('/usr/local/bin/python3.11 -m backend.commands.holding_distribution')

@task
def noteworthy(ctx):
    ctx.run('/usr/local/bin/python3.11 -m backend.commands.noteworthy_addresses')
@task
def top(ctx):
    ctx.run('/usr/local/bin/python3.11 -m backend.commands.top_holders_holdings')

