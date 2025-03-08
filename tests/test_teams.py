"""
Microsoft Teams通知のユニットテスト
"""

import json
import unittest
from unittest.mock import ANY, MagicMock, patch

import requests

from zangetsu_notification.teams import TeamsNotification


class TestTeamsNotification(unittest.TestCase):
    """TeamsNotificationクラスのテスト"""

    def setUp(self):
        """テスト前の共通セットアップ"""
        self.webhook_url = "https://outlook.office.com/webhook/TEST/TEST/TEST"

    def tearDown(self):
        """テスト後のクリーンアップ"""
        pass

    def test_init(self):
        """TeamsNotificationの初期化テスト"""
        # 環境変数から取得
        with patch("os.getenv", MagicMock(return_value="https://teams.webhook.url")):
            teams = TeamsNotification()
            self.assertEqual(teams.webhook_url, "https://teams.webhook.url")

        # 引数で指定
        teams = TeamsNotification(webhook_url=self.webhook_url)
        self.assertEqual(teams.webhook_url, self.webhook_url)

        # 値が指定されておらず、環境変数もない場合
        with patch("os.getenv", MagicMock(return_value=None)):
            with self.assertRaises(ValueError):
                TeamsNotification()

    @patch("requests.post")
    def test_send_message(self, mock_post):
        """メッセージ送信のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        teams = TeamsNotification(webhook_url=self.webhook_url)
        result = teams.send_message(
            message="テストメッセージ",
            title="テストタイトル",
            subtitle="テストサブタイトル",
            theme_color="FF0000",
        )

        # アサーション
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            self.webhook_url, data=ANY, headers={"Content-Type": "application/json"}
        )

        # 送信データの検証
        args, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["@type"], "MessageCard")
        self.assertEqual(payload["themeColor"], "FF0000")

        # セクションの確認
        self.assertGreaterEqual(len(payload["sections"]), 1)
        section_found = False
        for section in payload["sections"]:
            if (
                "activityTitle" in section
                and section["activityTitle"] == "テストタイトル"
            ):
                self.assertEqual(section["activitySubtitle"], "テストサブタイトル")
                section_found = True
        self.assertTrue(
            section_found, "タイトルとサブタイトルを含むセクションが見つかりません"
        )

        # メッセージテキストの確認
        message_found = False
        for section in payload["sections"]:
            if "text" in section and section["text"] == "テストメッセージ":
                message_found = True
        self.assertTrue(message_found, "メッセージテキストが見つかりません")

    @patch("requests.post")
    def test_send_message_minimal(self, mock_post):
        """最小限のパラメータでのメッセージ送信テスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        teams = TeamsNotification(webhook_url=self.webhook_url)
        result = teams.send_message("テストメッセージ")

        # アサーション
        self.assertTrue(result)
        args, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])

        # 基本的な構造の確認
        self.assertEqual(payload["@type"], "MessageCard")
        self.assertEqual(payload["summary"], "通知")

        # メッセージテキストの確認
        message_found = False
        for section in payload["sections"]:
            if "text" in section and section["text"] == "テストメッセージ":
                message_found = True
        self.assertTrue(message_found, "メッセージテキストが見つかりません")

    @patch("requests.post")
    def test_send_message_error(self, mock_post):
        """メッセージ送信エラーのテスト"""
        # モックの設定
        mock_post.side_effect = requests.RequestException("テストエラー")

        # テスト実行
        teams = TeamsNotification(webhook_url=self.webhook_url)
        result = teams.send_message("テストメッセージ")

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
        teams = TeamsNotification(webhook_url=self.webhook_url)
        result = teams.send_error_message(
            error_message="テストエラー", error_details="エラーの詳細"
        )

        # アサーション
        self.assertTrue(result)
        args, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])

        # エラーメッセージの確認
        self.assertEqual(payload["summary"], "エラーが発生しました")
        self.assertEqual(payload["themeColor"], "FF0000")

        # タイトルセクションの確認
        title_found = False
        for section in payload["sections"]:
            if (
                "activityTitle" in section
                and section["activityTitle"] == "エラーが発生しました"
            ):
                title_found = True
        self.assertTrue(title_found, "エラータイトルが見つかりません")

        # メッセージとエラー詳細の確認
        message_text = None
        for section in payload["sections"]:
            if "text" in section and "エラーの詳細" in section["text"]:
                message_text = section["text"]

        self.assertIsNotNone(message_text, "エラー詳細が見つかりません")
        self.assertIn("テストエラー", message_text)

    @patch("requests.post")
    def test_send_success_message(self, mock_post):
        """成功メッセージ送信のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        teams = TeamsNotification(webhook_url=self.webhook_url)
        result = teams.send_success_message(
            success_message="テスト成功", additional_info="追加情報"
        )

        # アサーション
        self.assertTrue(result)
        args, kwargs = mock_post.call_args
        payload = json.loads(kwargs["data"])

        # 成功メッセージの確認
        self.assertEqual(payload["summary"], "処理が成功しました")
        self.assertEqual(payload["themeColor"], "00FF00")

        # タイトルセクションの確認
        title_found = False
        for section in payload["sections"]:
            if (
                "activityTitle" in section
                and section["activityTitle"] == "処理が成功しました"
            ):
                title_found = True
        self.assertTrue(title_found, "成功タイトルが見つかりません")

        # メッセージと追加情報の確認
        message_text = None
        for section in payload["sections"]:
            if "text" in section and "追加情報" in section["text"]:
                message_text = section["text"]

        self.assertIsNotNone(message_text, "追加情報が見つかりません")
        self.assertIn("テスト成功", message_text)


if __name__ == "__main__":
    unittest.main()
