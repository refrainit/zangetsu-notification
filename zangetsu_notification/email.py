import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from zangetsu_notification.base import NotificationBase


class EmailNotification(NotificationBase):
    """
    Eメールによる通知を送信するユーティリティクラス

    SMTPサーバー経由でメール通知を送信します。
    """

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        sender_email: Optional[str] = None,
        use_tls: bool = True,
    ):
        """
        Eメール通知クラスの初期化

        Args:
            smtp_server (Optional[str]): SMTPサーバーアドレス
                指定しない場合は環境変数から取得
            smtp_port (Optional[int]): SMTPポート
                指定しない場合は環境変数から取得
            smtp_username (Optional[str]): SMTP認証ユーザー名
                指定しない場合は環境変数から取得
            smtp_password (Optional[str]): SMTP認証パスワード
                指定しない場合は環境変数から取得
            sender_email (Optional[str]): 送信元メールアドレス
                指定しない場合は環境変数またはsmtp_usernameを使用
            use_tls (bool): TLS暗号化を使用するかどうか

        Raises:
            ValueError: 必要な設定が不足している場合
        """
        super().__init__()

        # 環境変数またはデフォルト値を使用
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER")

        # SMTPポートの取得（エラー処理を追加）
        smtp_port_str = os.getenv("SMTP_PORT")
        default_port = 587
        if smtp_port is not None:
            self.smtp_port = smtp_port
        elif smtp_port_str:
            try:
                self.smtp_port = int(smtp_port_str)
            except (ValueError, TypeError):
                self.smtp_port = default_port
        else:
            self.smtp_port = default_port

        self.smtp_username = smtp_username or os.getenv("SMTP_USERNAME")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.sender_email = (
            sender_email or os.getenv("SENDER_EMAIL") or self.smtp_username
        )
        self.use_tls = use_tls

        # 必須パラメータのチェック
        if not all(
            [
                self.smtp_server,
                self.smtp_username,
                self.smtp_password,
                self.sender_email,
            ]
        ):
            missing = []
            if not self.smtp_server:
                missing.append("SMTPサーバー")
            if not self.smtp_username:
                missing.append("SMTPユーザー名")
            if not self.smtp_password:
                missing.append("SMTPパスワード")
            if not self.sender_email:
                missing.append("送信元メールアドレス")

            raise ValueError(
                f"Eメール通知の設定が不足しています: {', '.join(missing)}。"
                "環境変数または初期化時にパラメータを指定してください。"
            )

    def send_message(
        self,
        message: str,
        subject: str = "通知",
        recipients: Optional[List[str]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        html_message: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """
        Eメールメッセージを送信する

        Args:
            message (str): 送信するメッセージ本文 (プレーンテキスト)
            subject (str): メールの件名
            recipients (Optional[List[str]]): 宛先メールアドレスのリスト
                指定しない場合は環境変数DEFAULT_RECIPIENTSから取得
            cc (Optional[List[str]]): CCメールアドレスのリスト
            bcc (Optional[List[str]]): BCCメールアドレスのリスト
            html_message (Optional[str]): HTMLフォーマットのメッセージ本文
            **kwargs: その他の引数

        Returns:
            bool: メッセージ送信の成否
        """
        # 受信者の取得（パラメータまたは環境変数から）
        if not recipients:
            default_recipients = os.getenv("DEFAULT_EMAIL_RECIPIENTS")
            if default_recipients:
                recipients = [r.strip() for r in default_recipients.split(",")]
            else:
                raise ValueError("受信者メールアドレスが指定されていません")

        # メッセージの作成
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = ", ".join(recipients)

        if cc:
            msg["Cc"] = ", ".join(cc)

        # プレーンテキストバージョンの追加
        msg.attach(MIMEText(message, "plain", "utf-8"))

        # HTMLバージョンの追加（指定されている場合）
        if html_message:
            msg.attach(MIMEText(html_message, "html", "utf-8"))

        # すべての受信者（To + CC + BCC）のリスト
        all_recipients = []
        all_recipients.extend(recipients)
        if cc:
            all_recipients.extend(cc)
        if bcc:
            all_recipients.extend(bcc)

        try:
            # SMTPサーバーへの接続
            smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
            smtp.ehlo()

            # TLS暗号化（必要に応じて）
            if self.use_tls:
                smtp.starttls()
                smtp.ehlo()

            # SMTP認証
            smtp.login(self.smtp_username, self.smtp_password)

            # メール送信
            smtp.sendmail(self.sender_email, all_recipients, msg.as_string())

            # 接続終了
            smtp.quit()
            return True

        except Exception as e:
            print(f"メールの送信中にエラーが発生しました: {e}")
            return False

    def send_error_message(
        self,
        error_message: str,
        error_details: Optional[str] = None,
        recipients: Optional[List[str]] = None,
        **kwargs,
    ) -> bool:
        """
        エラー通知用のメールを送信する

        Args:
            error_message (str): エラーの概要
            error_details (Optional[str]): エラーの詳細情報
            recipients (Optional[List[str]]): 宛先メールアドレスのリスト
            **kwargs: その他の引数

        Returns:
            bool: メッセージ送信の成否
        """
        subject = "【エラー】" + error_message

        # プレーンテキストメッセージ
        plain_message = f"エラーが発生しました: {error_message}\n\n"
        if error_details:
            plain_message += f"詳細情報:\n{error_details}"

        # HTMLメッセージ
        html_message = f"""
        <html>
        <body>
            <h2 style="color: #FF0000;">エラーが発生しました</h2>
            <p><strong>{error_message}</strong></p>
            
            {f"<h3>詳細情報:</h3><pre>{error_details}</pre>" if error_details else ""}
        </body>
        </html>
        """

        return self.send_message(
            message=plain_message,
            subject=subject,
            recipients=recipients,
            html_message=html_message,
            **kwargs,
        )

    def send_success_message(
        self,
        success_message: str,
        additional_info: Optional[str] = None,
        recipients: Optional[List[str]] = None,
        **kwargs,
    ) -> bool:
        """
        成功通知用のメールを送信する

        Args:
            success_message (str): 成功の概要
            additional_info (Optional[str]): 追加情報
            recipients (Optional[List[str]]): 宛先メールアドレスのリスト
            **kwargs: その他の引数

        Returns:
            bool: メッセージ送信の成否
        """
        subject = "【成功】" + success_message

        # プレーンテキストメッセージ
        plain_message = f"処理が成功しました: {success_message}\n\n"
        if additional_info:
            plain_message += f"追加情報:\n{additional_info}"

        # HTMLメッセージ
        html_message = f"""
        <html>
        <body>
            <h2 style="color: #007700;">処理が成功しました</h2>
            <p><strong>{success_message}</strong></p>
            
            {f"<h3>追加情報:</h3><p>{additional_info}</p>" if additional_info else ""}
        </body>
        </html>
        """

        return self.send_message(
            message=plain_message,
            subject=subject,
            recipients=recipients,
            html_message=html_message,
            **kwargs,
        )
