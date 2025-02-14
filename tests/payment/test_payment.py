from dotenv import load_dotenv
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

load_dotenv()
import sys
import os

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, root_path)

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
    @patch("backend.bot.paywall.payment.insert_user")
    def test_check_user_existing(
        self,
        mock_insert_user,
        mock_update_user,
        mock_generate_wallet,
        mock_fetch_user_by_id,
    ):
        mock_fetch_user_by_id.return_value = pd.DataFrame(
            {"user_id": ["123"], "public_key": ["some_public_key"]}
        )
        result = check_user("123", "ref_info")
        assert result == "some_public_key"
        mock_generate_wallet.assert_not_called()
        mock_update_user.assert_not_called()
        mock_insert_user.assert_not_called()

    @pytest.mark.only
    @patch("backend.bot.paywall.payment.fetch_user_by_id")
    # @patch("backend.bot.paywall.payment.generate_wallet")
    # @patch("backend.bot.paywall.payment.update_user")
    # @patch("backend.bot.paywall.payment.insert_user")
    def test_check_user_new(
        self,
        # mock_insert_user,
        # mock_update_user,
        # mock_generate_wallet,
        mock_fetch_user_by_id,
    ):
        mock_fetch_user_by_id.return_value = pd.DataFrame()
        # mock_generate_wallet.return_value = "new_public_key"
        check_user("123", "ref_info")
        # mock_insert_user.assert_called_once_with("123", 0, "ref_info")
        # mock_generate_wallet.assert_called_once_with("123")
        # mock_update_user.assert_called()

    # @pytest.mark.skip
    @patch("backend.bot.paywall.payment.Client")
    @patch("backend.bot.paywall.payment.get_rpc")
    def test_check_balance(self, mock_get_rpc, mock_client):
        mock_get_rpc.return_value = "mock_rpc_url"
        mock_client_instance = mock_client.return_value
        mock_client_instance.get_account_info.return_value = MagicMock(
            value=MagicMock(lamports=1000000000)
        )

        checked = check_balance("some_wallet_address")
        print("vvvv")
        print(checked)
        result, payed = checked
        assert result == "Balance for wallet some_wallet_address: 1.0 SOL "
        assert payed == 0

    @pytest.mark.skip
    @patch("backend.bot.paywall.payment.Client")
    @patch("backend.bot.paywall.payment.get_rpc")
    def test_check_balance_insufficient(self, mock_get_rpc, mock_client):
        mock_get_rpc.return_value = "mock_rpc_url"
        mock_client_instance = mock_client.return_value
        mock_client_instance.get_account_info.return_value = MagicMock(
            value=MagicMock(lamports=500000000)
        )

        result, payed = check_balance("some_wallet_address")
        assert "Please transfer 0.19 SOL and check again to unlock features" in result
        assert payed == 0

    @pytest.mark.skip
    @patch("backend.bot.paywall.payment.Client")
    @patch("backend.bot.paywall.payment.get_rpc")
    def test_check_balance_sufficient(self, mock_get_rpc, mock_client):
        mock_get_rpc.return_value = "mock_rpc_url"
        mock_client_instance = mock_client.return_value
        mock_client_instance.get_account_info.return_value = MagicMock(
            value=MagicMock(lamports=1000000000)
        )

        result, payed = check_balance("some_wallet_address")
        assert "Happy Trading! the features are now unlocked" in result
        assert payed == 1
