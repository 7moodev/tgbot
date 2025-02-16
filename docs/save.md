---

---
A calculation:
1. Getting trending tokens created within 24h with 1000+ holders
2. Goal: Get 10 tokens fulfilling (1.)
3. call GET /defi/token_trending with limit 20 (which is the maximum)
4. On those 20 tokens call GET defi/token_overview (30cu) and GET /defi/token_creation_info (30cu) --> 60*20 = 1200CU
5. Repeat 5 times to get the goal (2.) --> 6000CU
6. Tokens fulfilling (2.) I quite rare, so we have to potentially repeat 50 times --> 60000CU
---
>>>> _ >>>> ~ file: holders_avg_entry_price.py:10 ~ wallet: 9ep2dgRSyDzCthaxgZezpHDcYcEheVEaLAcwMwGq5Wp3
>>>> _ >>>> ~ file: holders_avg_entry_price.py:10 ~ token: 7ishPuuCB8KuBeM3ePCBfqyDHMc3aQoJ4DiKwc8HT5WH
>>>> _ >>>> ~ file: holders_avg_entry_price.py:10 ~ token_creation_time: 1712805992


---

timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP

---
https://docs.birdeye.so/reference/get_defi-token-trending
{
  "data": {
    "updateUnixTime": 1726681733,
    "updateTime": "2024-09-18T17:48:53",
    "tokens": [
      {
        "address": "HJXh1XULVe2Mdp6mTKd5K7of1uFqBTbmcWzvBv6cpump",
        "decimals": 6,
        "liquidity": 34641.80933146691,
        "logoURI": "https://img.fotofolio.xyz/?w=30&h=30&url=https%3A%2F%2Fipfs.io%2Fipfs%2FQmR7QnPaYcfwoG8oymK5JRDsB9GSgHr71mJmL2MuJ7Qk3x",
        "name": "AVOCATO",
        "symbol": "ATO",
        "volume24hUSD": 1202872.3148187269,
        "rank": 1,
        "price": 0.00010551649518689046
      },
      {
        "address": "HYFDwieKWth1kzKbtLFMtgMVwukyvyWNYFxyQDcWpump",
        "decimals": 6,
        "liquidity": 73874.80948083404,
        "logoURI": "https://img.fotofolio.xyz/?w=30&h=30&url=https%3A%2F%2Fipfs.io%2Fipfs%2FQmUxhHFAugzzWmTMCMCky1QjaJNjtpBNhC2iRELb77Vqfw",
        "name": "The Liquidator",
        "symbol": "LIQUIDATOR",
        "volume24hUSD": 920580.3615402475,
        "rank": 2,
        "price": 0.0006106216453936813
      }
    ],
    "total": 1000
  },
  "success": true
}

---
x api error
{
    "detail": "Authenticating with OAuth 2.0 Application-Only is forbidden for this endpoint.  Supported authentication types are [OAuth 1.0a User Context, OAuth 2.0 User Context].",
    "status": 403,
    "title": "Unsupported Authentication",
    "type": "https://api.twitter.com/2/problems/unsupported-authentication"
}

---
token_overview error
{
    "success": false,
    "message": "Unauthorized"
}

---
    # @patch("backend.bot.paywall.payment.fetch_user_by_id")
    # @patch("backend.bot.paywall.payment.generate_wallet")
    # @patch("backend.bot.paywall.payment.update_user")
    # def test_check_user_new(
    #     self, mock_update_user, mock_generate_wallet, mock_fetch_user_by_id
    # ):
    #     mock_fetch_user_by_id.return_value = pd.DataFrame()
    #     mock_generate_wallet.return_value = "new_public_key"
    #     check_user("123", "ref_info")
    #     mock_generate_wallet.assert_called_once_with("123")
    #     mock_update_user.assert_called()

    # @patch("backend.bot.paywall.payment.Client")
    # def test_check_balance(self, mock_client):
    #     mock_client_instance = mock_client.return_value
    #     mock_client_instance.get_account_info.return_value.value = MagicMock(
    #         lamports=690000000
    #     )
    #     response, payed = check_balance("some_wallet_address")
    #     assert response == "Happy Trading! the features are now unlocked"
    #     assert payed == 1

    # @patch("backend.bot.paywall.payment.Client")
    # def test_check_balance_insufficient(self, mock_client):
    #     mock_client_instance = mock_client.return_value
    #     mock_client_instance.get_account_info.return_value.value = MagicMock(
    #         lamports=100000000
    #     )
    #     response, payed = check_balance("some_wallet_address")
    #     assert "Please transfer" in response
    #     assert payed == 0

    # @patch("backend.bot.paywall.payment.fetch_user_by_id")
    # def test_get_user_info(self, mock_fetch_user_by_id):
    #     mock_fetch_user_by_id.return_value = pd.DataFrame(
    #         {
    #             "user_id": ["123"],
    #             "public_key": ["some_public_key"],
    #             "expiration_date": [None],
    #         }
    #     ).set_index("user_id")
    #     result = get_user_info("123")
    #     assert result["public_key"] == "some_public_key"

    # @patch("backend.bot.paywall.payment.check_balance")
    # @patch("backend.bot.paywall.payment.get_user_info")
    # @patch("backend.bot.paywall.payment.update_user")
    # def test_grant_access(
    #     self, mock_update_user, mock_get_user_info, mock_check_balance
    # ):
    #     mock_get_user_info.return_value = {
    #         "public_key": "some_public_key",
    #         "expiration_date": None,
    #         "referred_by": None,
    #     }
    #     mock_check_balance.return_value = (
    #         "Happy Trading! the features are now unlocked",
    #         1,
    #     )
    #     response = grant_access("123")
    #     assert "Happy Trading!" in response
    #     mock_update_user.assert_called()

    # @patch("backend.bot.paywall.payment.get_user_info")
    # def test_check_access(self, mock_get_user_info):
    #     mock_get_user_info.return_value = {
    #         "expiration_date": (datetime.now() + timedelta(days=1)).strftime(
    #             "%Y-%m-%d %H:%M:%S.%f"
    #         )
    #     }
    #     assert check_access("123") == True

    # @patch("backend.bot.paywall.payment.get_user_info")
    # def test_check_access_expired(self, mock_get_user_info):
    #     mock_get_user_info.return_value = {
    #         "expiration_date": (datetime.now() - timedelta(days=1)).strftime(
    #             "%Y-%m-%d %H:%M:%S.%f"
    #         )
    #     }
    #     assert check_access("123") == False

    # @patch("backend.bot.paywall.payment.update_user")
    # def test_deposit_wallet(self, mock_update_user):
    #     response = deposit_wallet("123", "new_wallet_address")
    #     assert "Reward wallet updated to" in response
    #     mock_update_user.assert_called_once_with(
    #         "deposit_wallet", "new_wallet_address", "123"
    #     )


---
        ON CONFLICT (id) DO UPDATE SET
            amount = EXCLUDED.amount,
            decimals = EXCLUDED.decimals,
            mint = EXCLUDED.mint,
            owner = EXCLUDED.owner,
            token_account = EXCLUDED.token_account,
            ui_amount = EXCLUDED.ui_amount
