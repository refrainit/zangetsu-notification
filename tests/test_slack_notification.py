"""
Slack通知のユニットテスト
"""

import json
import unittest
from unittest.mock import ANY, MagicMock, patch

import requests

from zangetsu_notification.slack import SlackNotification


class TestSlackNotification(unittest.TestCase):
    """SlackNotificationクラスのテスト"""

    def setUp(self):
        """テスト前の共通セットアップ"""
        self.webhook_url = "https://hooks.slack.com/services/TEST/TEST/TEST"

    def tearDown(self):
        """テスト後のクリーンアップ"""
        pass

    def test_init(self):
        """SlackNotificationの初期化テスト"""
        # 環境変数から取得
        with patch("os.getenv", MagicMock(return_value="https://slack.com/webhook")):
            slack = SlackNotification()
            self.assertEqual(slack.webhook_url, "https://slack.com/webhook")

        # 引数で指定
        slack = SlackNotification(webhook_url=self.webhook_url)
        self.assertEqual(slack.webhook_url, self.webhook_url)

        # 値が指定されておらず、環境変数もない場合
        with patch("os.getenv", MagicMock(return_value=None)):
            with self.assertRaises(ValueError):
                SlackNotification()

    def test_format_mention(self):
        """メンションのフォーマットテスト"""
        slack = SlackNotification(webhook_url=self.webhook_url)

        # すでに正しいフォーマットの場合
        self.assertEqual(slack._format_mention("<@U12345>"), "<@U12345>")

        # ユーザーIDの場合
        self.assertEqual(slack._format_mention("U12345678"), "<@U12345678>")

        # メールアドレスの場合
        self.assertEqual(slack._format_mention("test@example.com"), "test@example.com")

        # 名前の場合
        self.assertEqual(slack._format_mention("John Doe"), "John Doe")

    @patch("requests.post")
    def test_send_message(self, mock_post):
        """メッセージ送信のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        slack = SlackNotification(webhook_url=self.webhook_url)
        result = slack.send_message(
            message="テストメッセージ",
            username="テストユーザー",
            icon_emoji=":test:",
            channel="#test-channel",
        )

        # アサーション
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            self.webhook_url, data=ANY, headers={"Content-Type": "application/json"}
        )

        # 送信データの検証（JSONをパースして内容を確認）
        args, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["text"], "テストメッセージ")
        self.assertEqual(payload["username"], "テストユーザー")
        self.assertEqual(payload["icon_emoji"], ":test:")
        self.assertEqual(payload["channel"], "#test-channel")

    @patch("requests.post")
    def test_send_message_with_mentions(self, mock_post):
        """メンション付きメッセージ送信のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        slack = SlackNotification(webhook_url=self.webhook_url)
        result = slack.send_message(
            message="テストメッセージ", mentions=["U12345678", "test@example.com"]
        )

        # アサーション
        self.assertTrue(result)
        args, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])
        # メンションが含まれていることを確認
        self.assertTrue(payload["text"].startswith("<@U12345678> test@example.com"))

    @patch("requests.post")
    def test_send_message_error(self, mock_post):
        """メッセージ送信エラーのテスト"""
        # モックの設定
        mock_post.side_effect = requests.RequestException("テストエラー")

        # テスト実行
        slack = SlackNotification(webhook_url=self.webhook_url)
        result = slack.send_message("テストメッセージ")

        # アサーション
        self.assertFalse(result)

    @patch("requests.post")
    def test_send_error_message(self, mock_post):
        """エラーメッセージ送信のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        slack = SlackNotification(webhook_url=self.webhook_url)
        result = slack.send_error_message(
            error_message="テストエラー",
            error_details="エラーの詳細",
            username="エラーボット",
            icon_emoji=":warning:",
        )

        # アサーション
        self.assertTrue(result)
        args, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])

        # テキストと添付ファイルを確認
        self.assertEqual(payload["text"], "*エラーが発生しました*: テストエラー")
        self.assertEqual(payload["username"], "エラーボット")
        self.assertEqual(payload["icon_emoji"], ":warning:")
        self.assertEqual(len(payload["attachments"]), 1)
        self.assertEqual(payload["attachments"][0]["color"], "danger")
        self.assertEqual(payload["attachments"][0]["title"], "エラー詳細")
        self.assertEqual(payload["attachments"][0]["text"], "エラーの詳細")

    @patch("requests.post")
    def test_send_success_message(self, mock_post):
        """成功メッセージ送信のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        slack = SlackNotification(webhook_url=self.webhook_url)
        result = slack.send_success_message(
            success_message="テスト成功",
            additional_info="追加情報",
            username="成功ボット",
            icon_emoji=":white_check_mark:",
        )

        # アサーション
        self.assertTrue(result)
        args, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])

        # テキストと添付ファイルを確認
        self.assertEqual(payload["text"], "*成功*: テスト成功")
        self.assertEqual(payload["username"], "成功ボット")
        self.assertEqual(payload["icon_emoji"], ":white_check_mark:")
        self.assertEqual(len(payload["attachments"]), 1)
        self.assertEqual(payload["attachments"][0]["color"], "good")
        self.assertEqual(payload["attachments"][0]["title"], "追加情報")
        self.assertEqual(payload["attachments"][0]["text"], "追加情報")


if __name__ == "__main__":
    unittest.main()
