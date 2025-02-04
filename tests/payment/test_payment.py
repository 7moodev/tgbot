import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd


from backend.bot.paywall.payment import (
    check_user,
    generate_wallet,
    check_balance,
    get_user_info,
    grant_access,
    check_access,
    deposit_wallet,
)


class TestPayment:

    @patch("backend.bot.paywall.payment.fetch_user_by_id")
    @patch("backend.bot.paywall.payment.generate_wallet")
    @patch("backend.bot.paywall.payment.update_user")
    def test_check_user_existing(
        self, mock_update_user, mock_generate_wallet, mock_fetch_user_by_id
    ):
        mock_fetch_user_by_id.return_value = pd.DataFrame(
            {"user_id": ["123"], "public_key": ["some_public_key"]}
        )
        result = check_user("123", "ref_info")
        assert result == "some_public_key"
        mock_generate_wallet.assert_not_called()
        mock_update_user.assert_not_called()

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
