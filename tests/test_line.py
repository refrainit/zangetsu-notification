"""
LINE Notify通知のユニットテスト
"""

import unittest
from unittest.mock import MagicMock, patch

import requests

from zangetsu_notification.line import LineNotification


class TestLineNotification(unittest.TestCase):
    """LineNotificationクラスのテスト"""

    def setUp(self):
        """テスト前の共通セットアップ"""
        self.access_token = "test_access_token"
        self.api_url = "https://notify-api.line.me/api/notify"

    def tearDown(self):
        """テスト後のクリーンアップ"""
        pass

    def test_init(self):
        """LineNotificationの初期化テスト"""
        # 環境変数から取得
        with patch("os.getenv", MagicMock(return_value="env_access_token")):
            line = LineNotification()
            self.assertEqual(line.access_token, "env_access_token")

        # 引数で指定
        line = LineNotification(access_token=self.access_token)
        self.assertEqual(line.access_token, self.access_token)

        # 値が指定されておらず、環境変数もない場合
        with patch("os.getenv", MagicMock(return_value=None)):
            with self.assertRaises(ValueError):
                LineNotification()

    @patch("requests.post")
    def test_send_message(self, mock_post):
        """メッセージ送信のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        line = LineNotification(access_token=self.access_token)
        result = line.send_message(
            message="テストメッセージ",
            image_url="https://example.com/image.jpg",
            image_thumbnail="https://example.com/thumbnail.jpg",
            sticker_package_id=1,
            sticker_id=2,
        )

        # アサーション
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            LineNotification.API_URL,
            headers={"Authorization": f"Bearer {self.access_token}"},
            data={
                "message": "テストメッセージ",
                "imageFullsize": "https://example.com/image.jpg",
                "imageThumbnail": "https://example.com/thumbnail.jpg",
                "stickerPackageId": 1,
                "stickerId": 2,
            },
        )

    @patch("requests.post")
    def test_send_message_only_text(self, mock_post):
        """テキストのみのメッセージ送信テスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        line = LineNotification(access_token=self.access_token)
        result = line.send_message("テストメッセージ")

        # アサーション
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            LineNotification.API_URL,
            headers={"Authorization": f"Bearer {self.access_token}"},
            data={"message": "テストメッセージ"},
        )

    @patch("requests.post")
    def test_send_message_with_image(self, mock_post):
        """画像付きメッセージ送信テスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        line = LineNotification(access_token=self.access_token)
        result = line.send_message(
            message="テストメッセージ", image_url="https://example.com/image.jpg"
        )

        # アサーション
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            LineNotification.API_URL,
            headers={"Authorization": f"Bearer {self.access_token}"},
            data={
                "message": "テストメッセージ",
                "imageFullsize": "https://example.com/image.jpg",
                "imageThumbnail": "https://example.com/image.jpg",
            },
        )

    @patch("requests.post")
    def test_send_message_error(self, mock_post):
        """メッセージ送信エラーのテスト"""
        # モックの設定
        mock_post.side_effect = requests.RequestException("テストエラー")

        # テスト実行
        line = LineNotification(access_token=self.access_token)
        result = line.send_message("テストメッセージ")

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
        line = LineNotification(access_token=self.access_token)
        result = line.send_error_message(
            error_message="テストエラー", error_details="エラーの詳細"
        )

        # アサーション
        self.assertTrue(result)
        args, kwargs = mock_post.call_args

        # メッセージ内容の確認
        self.assertEqual(args[0], LineNotification.API_URL)
        self.assertEqual(
            kwargs["headers"], {"Authorization": f"Bearer {self.access_token}"}
        )
        self.assertIn("⚠", kwargs["data"]["message"])
        self.assertIn("テストエラー", kwargs["data"]["message"])
        self.assertIn("エラーの詳細", kwargs["data"]["message"])

    @patch("requests.post")
    def test_send_success_message(self, mock_post):
        """成功メッセージ送信のテスト"""
        # モックの設定
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # テスト実行
        line = LineNotification(access_token=self.access_token)
        result = line.send_success_message(
            success_message="テスト成功", additional_info="追加情報"
        )

        # アサーション
        self.assertTrue(result)
        args, kwargs = mock_post.call_args

        # メッセージ内容の確認
        self.assertEqual(args[0], LineNotification.API_URL)
        self.assertEqual(
            kwargs["headers"], {"Authorization": f"Bearer {self.access_token}"}
        )
        self.assertIn("✅", kwargs["data"]["message"])
        self.assertIn("テスト成功", kwargs["data"]["message"])
        self.assertIn("追加情報", kwargs["data"]["message"])


if __name__ == "__main__":
    unittest.main()
