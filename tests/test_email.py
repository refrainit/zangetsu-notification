"""
メール通知のユニットテスト
"""

import email
import smtplib
import unittest
from unittest.mock import MagicMock, patch

from zangetsu_notification.email import EmailNotification


class TestEmailNotification(unittest.TestCase):
    """EmailNotificationクラスのテスト"""

    def setUp(self):
        """テスト前の共通セットアップ"""
        self.smtp_server = "smtp.example.com"
        self.smtp_port = 587
        self.smtp_username = "test@example.com"
        self.smtp_password = "password123"
        self.sender_email = "sender@example.com"

    def tearDown(self):
        """テスト後のクリーンアップ"""
        pass

    def test_init(self):
        """EmailNotificationの初期化テスト"""
        # 引数で直接指定
        email_notifier = EmailNotification(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            smtp_username=self.smtp_username,
            smtp_password=self.smtp_password,
            sender_email=self.sender_email,
        )

        self.assertEqual(email_notifier.smtp_server, self.smtp_server)
        self.assertEqual(email_notifier.smtp_port, self.smtp_port)
        self.assertEqual(email_notifier.smtp_username, self.smtp_username)
        self.assertEqual(email_notifier.smtp_password, self.smtp_password)
        self.assertEqual(email_notifier.sender_email, self.sender_email)
        self.assertTrue(email_notifier.use_tls)

        # 環境変数から取得
        env_patch = {
            "SMTP_SERVER": "env-smtp.example.com",
            "SMTP_PORT": "25",
            "SMTP_USERNAME": "env-test@example.com",
            "SMTP_PASSWORD": "env-password",
            "SENDER_EMAIL": "env-sender@example.com",
        }

        with patch.dict("os.environ", env_patch):
            with patch("os.getenv") as mock_getenv:
                # 環境変数から値を返すように設定
                def getenv_side_effect(key, default=None):
                    return env_patch.get(key, default)

                mock_getenv.side_effect = getenv_side_effect

                email_notifier = EmailNotification()
                self.assertEqual(email_notifier.smtp_server, "env-smtp.example.com")
                self.assertEqual(email_notifier.smtp_port, 25)
                self.assertEqual(email_notifier.smtp_username, "env-test@example.com")
                self.assertEqual(email_notifier.smtp_password, "env-password")
                self.assertEqual(email_notifier.sender_email, "env-sender@example.com")

        # 必須パラメータが不足している場合
        with patch("os.getenv", return_value=None):
            with self.assertRaises(ValueError):
                EmailNotification()

    @patch("smtplib.SMTP")
    def test_send_message(self, mock_smtp):
        """メッセージ送信のテスト"""
        # モックの設定
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        # テスト実行
        email_notifier = EmailNotification(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            smtp_username=self.smtp_username,
            smtp_password=self.smtp_password,
            sender_email=self.sender_email,
        )

        result = email_notifier.send_message(
            message="テストメッセージ",
            subject="テスト件名",
            recipients=["recipient@example.com"],
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            html_message="<p>HTMLメッセージ</p>",
        )

        # アサーション
        self.assertTrue(result)

        # SMTPクライアントが正しく使用されたか確認
        mock_smtp.assert_called_once_with(self.smtp_server, self.smtp_port)
        mock_smtp_instance.ehlo.assert_called()
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(
            self.smtp_username, self.smtp_password
        )

        # sendmailの呼び出しを確認
        mock_smtp_instance.sendmail.assert_called_once()
        args, kwargs = mock_smtp_instance.sendmail.call_args

        # 送信元と送信先の確認
        self.assertEqual(args[0], self.sender_email)
        self.assertEqual(len(args[1]), 3)  # 3人の受信者 (To, CC, BCC)
        self.assertIn("recipient@example.com", args[1])
        self.assertIn("cc@example.com", args[1])
        self.assertIn("bcc@example.com", args[1])

        # メッセージ内容を解析して確認
        message_str = args[2]
        message = email.message_from_string(message_str)

        # 件名がBase64エンコードされているため、ヘッダーのみを確認
        self.assertTrue(message["Subject"].startswith("=?utf-8?"))
        self.assertEqual(message["From"], self.sender_email)
        self.assertEqual(message["To"], "recipient@example.com")
        self.assertEqual(message["Cc"], "cc@example.com")

        # マルチパートメッセージであることを確認
        self.assertTrue(message.is_multipart())

        # 各パートの内容を確認
        parts = message.get_payload()
        self.assertEqual(len(parts), 2)  # プレーンテキストとHTML

        # プレーンテキストパートがあることを確認
        text_part_found = False
        html_part_found = False
        for part in parts:
            if part.get_content_type() == "text/plain":
                text_part_found = True
            elif part.get_content_type() == "text/html":
                html_part_found = True

        self.assertTrue(text_part_found, "プレーンテキストパートが見つかりません")
        self.assertTrue(html_part_found, "HTMLパートが見つかりません")

    @patch("smtplib.SMTP")
    def test_send_message_with_default_recipients(self, mock_smtp):
        """デフォルト受信者でのメッセージ送信テスト"""
        # モックの設定
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        # 環境変数の設定
        with patch(
            "os.getenv", return_value="default1@example.com,default2@example.com"
        ):
            # テスト実行
            email_notifier = EmailNotification(
                smtp_server=self.smtp_server,
                smtp_port=self.smtp_port,
                smtp_username=self.smtp_username,
                smtp_password=self.smtp_password,
                sender_email=self.sender_email,
            )

            result = email_notifier.send_message(
                message="テストメッセージ", subject="テスト件名"
            )

            # アサーション
            self.assertTrue(result)

            # sendmailの呼び出しを確認
            mock_smtp_instance.sendmail.assert_called_once()
            args, kwargs = mock_smtp_instance.sendmail.call_args

            # 送信先の確認（デフォルト受信者）
            self.assertEqual(len(args[1]), 2)
            self.assertIn("default1@example.com", args[1])
            self.assertIn("default2@example.com", args[1])

    @patch("smtplib.SMTP")
    def test_send_message_error(self, mock_smtp):
        """メッセージ送信エラーのテスト"""
        # モックの設定
        mock_smtp.side_effect = smtplib.SMTPException("テストエラー")

        # テスト実行
        email_notifier = EmailNotification(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            smtp_username=self.smtp_username,
            smtp_password=self.smtp_password,
            sender_email=self.sender_email,
        )

        result = email_notifier.send_message(
            message="テストメッセージ",
            subject="テスト件名",
            recipients=["recipient@example.com"],
        )

        # アサーション
        self.assertFalse(result)

    @patch("smtplib.SMTP")
    def test_send_error_message(self, mock_smtp):
        """エラーメッセージ送信のテスト"""
        # モックの設定
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        # テスト実行
        email_notifier = EmailNotification(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            smtp_username=self.smtp_username,
            smtp_password=self.smtp_password,
            sender_email=self.sender_email,
        )

        result = email_notifier.send_error_message(
            error_message="テストエラー",
            error_details="エラーの詳細",
            recipients=["recipient@example.com"],
        )

        # アサーション
        self.assertTrue(result)

        # sendmailの呼び出しを確認
        mock_smtp_instance.sendmail.assert_called_once()
        args, kwargs = mock_smtp_instance.sendmail.call_args

        # メッセージ内容を解析して確認
        message_str = args[2]
        message = email.message_from_string(message_str)

        # 件名がBase64エンコードされているため、ヘッダーのみを確認
        self.assertTrue(message["Subject"].startswith("=?utf-8?"))

        # マルチパートメッセージであることを確認
        self.assertTrue(message.is_multipart())

        # デコードされたプレーンテキストの内容を確認
        for part in message.get_payload():
            if part.get_content_type() == "text/plain":
                payload_bytes = part.get_payload(decode=True)
                payload_text = payload_bytes.decode("utf-8")
                self.assertIn("エラーが発生しました", payload_text)
                self.assertIn("テストエラー", payload_text)
                self.assertIn("エラーの詳細", payload_text)
                break

    @patch("smtplib.SMTP")
    def test_send_success_message(self, mock_smtp):
        """成功メッセージ送信のテスト"""
        # モックの設定
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance

        # テスト実行
        email_notifier = EmailNotification(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            smtp_username=self.smtp_username,
            smtp_password=self.smtp_password,
            sender_email=self.sender_email,
        )

        result = email_notifier.send_success_message(
            success_message="テスト成功",
            additional_info="追加情報",
            recipients=["recipient@example.com"],
        )

        # アサーション
        self.assertTrue(result)

        # sendmailの呼び出しを確認
        mock_smtp_instance.sendmail.assert_called_once()
        args, kwargs = mock_smtp_instance.sendmail.call_args

        # メッセージ内容を解析して確認
        message_str = args[2]
        message = email.message_from_string(message_str)

        # 件名がBase64エンコードされているため、ヘッダーのみを確認
        self.assertTrue(message["Subject"].startswith("=?utf-8?"))

        # マルチパートメッセージであることを確認
        self.assertTrue(message.is_multipart())

        # デコードされたプレーンテキストの内容を確認
        for part in message.get_payload():
            if part.get_content_type() == "text/plain":
                payload_bytes = part.get_payload(decode=True)
                payload_text = payload_bytes.decode("utf-8")
                self.assertIn("処理が成功しました", payload_text)
                self.assertIn("テスト成功", payload_text)
                self.assertIn("追加情報", payload_text)
                break


if __name__ == "__main__":
    unittest.main()
