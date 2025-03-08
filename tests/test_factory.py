"""
通知ファクトリーのユニットテスト
"""

import unittest
from unittest.mock import MagicMock, patch

from zangetsu_notification.base import NotificationBase
from zangetsu_notification.email import EmailNotification
from zangetsu_notification.factory import (
    MultiNotifier,
    NotificationFactory,
    create_notifier,
    from_env,
)
from zangetsu_notification.line import LineNotification
from zangetsu_notification.slack import SlackNotification
from zangetsu_notification.teams import TeamsNotification
from zangetsu_notification.webhook import WebhookNotification


class TestNotificationFactory(unittest.TestCase):
    """NotificationFactoryクラスのテスト"""

    def test_create(self):
        """単一通知クラスの作成テスト"""
        # Slack
        with patch.object(
            SlackNotification, "__init__", return_value=None
        ) as mock_init:
            notifier = NotificationFactory.create(
                "slack", {"webhook_url": "https://example.com"}
            )
            self.assertIsInstance(notifier, SlackNotification)
            mock_init.assert_called_once_with(webhook_url="https://example.com")

        # Teams
        with patch.object(
            TeamsNotification, "__init__", return_value=None
        ) as mock_init:
            notifier = NotificationFactory.create(
                "teams", {"webhook_url": "https://teams.example.com"}
            )
            self.assertIsInstance(notifier, TeamsNotification)
            mock_init.assert_called_once_with(webhook_url="https://teams.example.com")

        # Email
        with patch.object(
            EmailNotification, "__init__", return_value=None
        ) as mock_init:
            notifier = NotificationFactory.create(
                "email", {"smtp_server": "smtp.example.com"}
            )
            self.assertIsInstance(notifier, EmailNotification)
            mock_init.assert_called_once_with(smtp_server="smtp.example.com")

        # LINE
        with patch.object(LineNotification, "__init__", return_value=None) as mock_init:
            notifier = NotificationFactory.create(
                "line", {"access_token": "test_token"}
            )
            self.assertIsInstance(notifier, LineNotification)
            mock_init.assert_called_once_with(access_token="test_token")

        # Webhook
        with patch.object(
            WebhookNotification, "__init__", return_value=None
        ) as mock_init:
            notifier = NotificationFactory.create(
                "webhook", {"webhook_url": "https://hook.example.com"}
            )
            self.assertIsInstance(notifier, WebhookNotification)
            mock_init.assert_called_once_with(webhook_url="https://hook.example.com")

        # サポートされていないタイプ
        with self.assertRaises(ValueError):
            NotificationFactory.create("unsupported")

    def test_create_multi(self):
        """複数通知クラスの作成テスト"""
        # モックの設定
        slack_mock = MagicMock(spec=SlackNotification)
        teams_mock = MagicMock(spec=TeamsNotification)

        with patch.object(NotificationFactory, "create") as mock_create:
            mock_create.side_effect = [slack_mock, teams_mock]

            # テスト実行
            notifiers = NotificationFactory.create_multi(
                ["slack", "teams"],
                {
                    "slack": {"webhook_url": "https://slack.example.com"},
                    "teams": {"webhook_url": "https://teams.example.com"},
                },
            )

            # アサーション
            self.assertEqual(len(notifiers), 2)
            self.assertIs(notifiers[0], slack_mock)
            self.assertIs(notifiers[1], teams_mock)

            # create呼び出しの確認
            mock_create.assert_any_call(
                "slack", {"webhook_url": "https://slack.example.com"}
            )
            mock_create.assert_any_call(
                "teams", {"webhook_url": "https://teams.example.com"}
            )

    def test_create_multi_with_error(self):
        """エラーが発生する複数通知クラスの作成テスト"""
        # モックの設定
        slack_mock = MagicMock(spec=SlackNotification)

        with patch.object(NotificationFactory, "create") as mock_create:
            # 最初は成功、2番目でエラー
            mock_create.side_effect = [slack_mock, ValueError("テストエラー")]

            # テスト実行（エラーに対して例外をキャッチするはず）
            notifiers = NotificationFactory.create_multi(["slack", "unknown"])

            # アサーション（エラーは無視され、成功したものだけ返される）
            self.assertEqual(len(notifiers), 1)
            self.assertIs(notifiers[0], slack_mock)


class TestMultiNotifier(unittest.TestCase):
    """MultiNotifierクラスのテスト"""

    def setUp(self):
        """テスト前の共通セットアップ"""
        # モック通知クラスの作成
        self.notifier1 = MagicMock(spec=NotificationBase)
        self.notifier2 = MagicMock(spec=NotificationBase)

        # テスト対象のインスタンス作成
        self.multi_notifier = MultiNotifier([self.notifier1, self.notifier2])

    def test_send_message(self):
        """複数通知先へのメッセージ送信テスト"""
        # モックの設定
        self.notifier1.send_message.return_value = True
        self.notifier2.send_message.return_value = True

        # テスト実行
        result = self.multi_notifier.send_message(
            message="テストメッセージ", extra_param="extra_value"
        )

        # アサーション
        self.assertTrue(result)
        self.notifier1.send_message.assert_called_once_with(
            message="テストメッセージ", extra_param="extra_value"
        )
        self.notifier2.send_message.assert_called_once_with(
            message="テストメッセージ", extra_param="extra_value"
        )

    def test_send_message_partial_failure(self):
        """一部の通知先で失敗するケースのテスト"""
        # モックの設定（1つ目は成功、2つ目は失敗）
        self.notifier1.send_message.return_value = True
        self.notifier2.send_message.return_value = False

        # テスト実行
        result = self.multi_notifier.send_message("テストメッセージ")

        # アサーション（一部失敗なのでFalseが返る）
        self.assertFalse(result)
        self.notifier1.send_message.assert_called_once_with(message="テストメッセージ")
        self.notifier2.send_message.assert_called_once_with(message="テストメッセージ")

    def test_send_message_with_exception(self):
        """例外が発生するケースのテスト"""
        # モックの設定（1つ目は成功、2つ目は例外発生）
        self.notifier1.send_message.return_value = True
        self.notifier2.send_message.side_effect = Exception("テストエラー")

        # テスト実行（例外は内部でキャッチされる）
        result = self.multi_notifier.send_message("テストメッセージ")

        # アサーション（例外が発生したのでFalseが返る）
        self.assertFalse(result)
        self.notifier1.send_message.assert_called_once_with(message="テストメッセージ")
        self.notifier2.send_message.assert_called_once_with(message="テストメッセージ")

    def test_send_error_message(self):
        """エラーメッセージの送信テスト"""
        # モックの設定
        self.notifier1.send_error_message.return_value = True
        self.notifier2.send_error_message.return_value = True

        # テスト実行
        result = self.multi_notifier.send_error_message(
            error_message="テストエラー", error_details="エラーの詳細"
        )

        # アサーション
        self.assertTrue(result)
        self.notifier1.send_error_message.assert_called_once_with(
            error_message="テストエラー", error_details="エラーの詳細"
        )
        self.notifier2.send_error_message.assert_called_once_with(
            error_message="テストエラー", error_details="エラーの詳細"
        )

    def test_send_success_message(self):
        """成功メッセージの送信テスト"""
        # モックの設定
        self.notifier1.send_success_message.return_value = True
        self.notifier2.send_success_message.return_value = True

        # テスト実行
        result = self.multi_notifier.send_success_message(
            success_message="テスト成功", additional_info="追加情報"
        )

        # アサーション
        self.assertTrue(result)
        self.notifier1.send_success_message.assert_called_once_with(
            success_message="テスト成功", additional_info="追加情報"
        )
        self.notifier2.send_success_message.assert_called_once_with(
            success_message="テスト成功", additional_info="追加情報"
        )


class TestHelperFunctions(unittest.TestCase):
    """ヘルパー関数のテスト"""

    @patch.object(NotificationFactory, "create")
    def test_create_notifier_single(self, mock_create):
        """単一通知クラス作成のヘルパー関数テスト"""
        mock_notifier = MagicMock(spec=SlackNotification)
        mock_create.return_value = mock_notifier

        # テスト実行
        notifier = create_notifier("slack", {"webhook_url": "https://example.com"})

        # アサーション
        self.assertIs(notifier, mock_notifier)
        mock_create.assert_called_once_with(
            "slack", {"webhook_url": "https://example.com"}
        )

    @patch.object(NotificationFactory, "create_multi")
    def test_create_notifier_multi(self, mock_create_multi):
        """複数通知クラス作成のヘルパー関数テスト"""
        mock_notifiers = [MagicMock(), MagicMock()]
        mock_create_multi.return_value = mock_notifiers

        # テスト実行
        notifier = create_notifier(
            ["slack", "email"],
            {
                "slack": {"webhook_url": "https://slack.example.com"},
                "email": {"smtp_server": "smtp.example.com"},
            },
        )

        # アサーション
        self.assertIsInstance(notifier, MultiNotifier)
        self.assertEqual(notifier.notifiers, mock_notifiers)
        mock_create_multi.assert_called_once_with(
            ["slack", "email"],
            {
                "slack": {"webhook_url": "https://slack.example.com"},
                "email": {"smtp_server": "smtp.example.com"},
            },
        )

    @patch("os.getenv")
    @patch("zangetsu_notification.factory.create_notifier")
    def test_from_env_single(self, mock_create_notifier, mock_getenv):
        """環境変数から単一通知クラスを作成するテスト"""
        mock_getenv.return_value = "slack"
        mock_notifier = MagicMock()
        mock_create_notifier.return_value = mock_notifier

        # テスト実行
        notifier = from_env()

        # アサーション
        self.assertIs(notifier, mock_notifier)
        mock_create_notifier.assert_called_once_with("slack")

    @patch("os.getenv")
    @patch("zangetsu_notification.factory.create_notifier")
    def test_from_env_multi(self, mock_create_notifier, mock_getenv):
        """環境変数から複数通知クラスを作成するテスト"""
        mock_getenv.return_value = "slack,email"
        mock_notifier = MagicMock()
        mock_create_notifier.return_value = mock_notifier

        # テスト実行
        notifier = from_env()

        # アサーション
        self.assertIs(notifier, mock_notifier)
        mock_create_notifier.assert_called_once_with(["slack", "email"])


if __name__ == "__main__":
    unittest.main()
