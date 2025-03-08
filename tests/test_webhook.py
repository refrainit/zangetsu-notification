"""
Webhook通知のユニットテスト
"""

import json
import unittest
from unittest.mock import MagicMock, patch

import requests

from zangetsu_notification.webhook import WebhookNotification


class TestWebhookNotification(unittest.TestCase):
    """WebhookNotificationクラスのテスト"""

    def setUp(self):
        """テスト前の共通セットアップ"""
        self.webhook_url = "https://example.com/webhook"
        self.headers = {"Authorization": "Bearer test_token"}
        self.default_payload = {"source": "test_app", "environment": "test"}

    def tearDown(self):
        """テスト後のクリーンアップ"""
        pass

    def test_init(self):
        """WebhookNotificationの初期化テスト"""
        # 環境変数から取得
        with patch(
            "os.getenv", MagicMock(return_value="https://env.example.com/webhook")
        ):
            webhook = WebhookNotification()
            self.assertEqual(webhook.webhook_url, "https://env.example.com/webhook")
            self.assertEqual(webhook.headers, {"Content-Type": "application/json"})
            self.assertEqual(webhook.default_payload, {})

        # 引数で指定
        webhook = WebhookNotification(
            webhook_url=self.webhook_url,
            headers=self.headers,
            default_payload=self.default_payload,
        )
        self.assertEqual(webhook.webhook_url, self.webhook_url)
        self.assertEqual(webhook.headers, self.headers)
        self.assertEqual(webhook.default_payload, self.default_payload)

        # 値が指定されておらず、環境変数もない場合
        with patch("os.getenv", MagicMock(return_value=None)):
            with self.assertRaises(ValueError):
                WebhookNotification()

    @patch("requests.post")
    def test_send_message(self, mock_post):
        """メッセージ送信のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        webhook = WebhookNotification(
            webhook_url=self.webhook_url,
            headers=self.headers,
            default_payload=self.default_payload,
        )

        result = webhook.send_message(
            message="テストメッセージ", payload={"priority": "high", "category": "test"}
        )

        # アサーション
        self.assertTrue(result)
        mock_post.assert_called_once()

        # 送信データの検証
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], self.webhook_url)
        self.assertEqual(kwargs["headers"], self.headers)

        # ペイロードの検証
        sent_payload = json.loads(kwargs["data"])
        self.assertEqual(sent_payload["message"], "テストメッセージ")
        self.assertEqual(sent_payload["source"], "test_app")  # デフォルトペイロードから
        self.assertEqual(
            sent_payload["environment"], "test"
        )  # デフォルトペイロードから
        self.assertEqual(sent_payload["priority"], "high")  # カスタムペイロードから
        self.assertEqual(sent_payload["category"], "test")  # カスタムペイロードから

    @patch("requests.post")
    def test_send_message_with_kwargs(self, mock_post):
        """追加のキーワード引数を使用したメッセージ送信テスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        webhook = WebhookNotification(webhook_url=self.webhook_url)

        result = webhook.send_message(
            message="テストメッセージ",
            extra_field="extra_value",
            timestamp="2023-01-01T12:00:00Z",
        )

        # アサーション
        self.assertTrue(result)

        # ペイロードの検証
        args, kwargs = mock_post.call_args
        sent_payload = json.loads(kwargs["data"])
        self.assertEqual(sent_payload["message"], "テストメッセージ")
        self.assertEqual(sent_payload["extra_field"], "extra_value")
        self.assertEqual(sent_payload["timestamp"], "2023-01-01T12:00:00Z")

    @patch("requests.post")
    def test_send_message_error(self, mock_post):
        """メッセージ送信エラーのテスト"""
        # モックの設定
        mock_post.side_effect = requests.RequestException("テストエラー")

        # テスト実行
        webhook = WebhookNotification(webhook_url=self.webhook_url)
        result = webhook.send_message("テストメッセージ")

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
        webhook = WebhookNotification(webhook_url=self.webhook_url)
        result = webhook.send_error_message(
            error_message="テストエラー", error_details="エラーの詳細"
        )

        # アサーション
        self.assertTrue(result)

        # ペイロードの検証
        args, kwargs = mock_post.call_args
        sent_payload = json.loads(kwargs["data"])
        self.assertEqual(sent_payload["message"], "テストエラー")
        self.assertEqual(sent_payload["type"], "error")
        self.assertEqual(sent_payload["title"], "エラーが発生しました")
        self.assertEqual(sent_payload["details"], "エラーの詳細")

    @patch("requests.post")
    def test_send_success_message(self, mock_post):
        """成功メッセージ送信のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        webhook = WebhookNotification(webhook_url=self.webhook_url)
        result = webhook.send_success_message(
            success_message="テスト成功", additional_info="追加情報"
        )

        # アサーション
        self.assertTrue(result)

        # ペイロードの検証
        args, kwargs = mock_post.call_args
        sent_payload = json.loads(kwargs["data"])
        self.assertEqual(sent_payload["message"], "テスト成功")
        self.assertEqual(sent_payload["type"], "success")
        self.assertEqual(sent_payload["title"], "処理が成功しました")
        self.assertEqual(sent_payload["details"], "追加情報")


if __name__ == "__main__":
    unittest.main()
