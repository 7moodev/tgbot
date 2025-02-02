# Commands

## /top

- topholders_command (tg_commands.py)
  - top_holders_holdings_parsed (parser.py)
    - get_top_holders_holdings (top_holders_holdings.py)
      - SolanaApiService.get_token_supply
      - BirdEyeApiService.get_top_holders
      - BirdEyeApiService.get_token_creation_info
      - BirdEyeApiService.get_token_overview
      - process_holder (top_holders_holdings.py)
        - get_wallet_portfolio
          = SolanaApiService.get_wallet_token_list
    - "backend/commands/outputs/top_holders_holdings.json"

## /fresh

- fresh_wallets_command (tg_commands.py)
  - fresh_wallets_parsed (parser.py)
    - fresh_wallets (fresh_wallets.py)
      - BirdEyeApiService.get_top_holders
      - BirdEyeApiService.get_token_overview
      - (not used) BirdEyeApiService.get_token_creation_info
    - offline
      - "backend/commands/outputs/fresh_wallets.json"

# Explanations

## context.user_data

- main2.py
  context.user_data.get('top_holders_started', False)

# Links

- https://docs.birdeye.so/
