import json
import os
from typing import Optional

import requests

from zangetsu_notification.base import NotificationBase


class TeamsNotification(NotificationBase):
    """
    Microsoft Teamsに通知を送信するユーティリティクラス

    環境変数やコンフィグからWebhook URLを取得し、
    メッセージ送信を可能にします。
    """

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Microsoft Teams通知クラスの初期化

        Args:
            webhook_url (Optional[str]): TeamsのWebhook URL
                指定しない場合は環境変数から取得を試みます

        Raises:
            ValueError: Webhook URLが見つからない場合
        """
        super().__init__()

        # webhook_urlが指定されていない場合は環境変数から取得
        if webhook_url is None:
            webhook_url = os.getenv("TEAMS_WEBHOOK_URL")

        if not webhook_url:
            raise ValueError(
                "Microsoft Teams Webhook URLが指定されていません。"
                "環境変数TEAMS_WEBHOOK_URLを設定するか、"
                "コンストラクタに直接URLを渡してください。"
            )

        self.webhook_url = webhook_url

    def send_message(
        self,
        message: str,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        theme_color: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """
        Microsoft Teamsにメッセージを送信する

        Args:
            message (str): 送信するメッセージ本文
            title (Optional[str]): カードのタイトル
            subtitle (Optional[str]): カードのサブタイトル
            theme_color (Optional[str]): カードのテーマカラー (16進数カラーコード)
            **kwargs: その他の引数

        Returns:
            bool: メッセージ送信の成否
        """
        # Teams用のカードを作成
        card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": title or "通知",
        }

        # テーマカラーが指定されている場合
        if theme_color:
            card["themeColor"] = theme_color

        # セクションの作成
        sections = []

        # タイトルやサブタイトルを含むセクション
        if title or subtitle:
            header_section = {}

            if title:
                header_section["activityTitle"] = title

            if subtitle:
                header_section["activitySubtitle"] = subtitle

            sections.append(header_section)

        # メッセージ本文を含むセクション
        message_section = {"text": message}
        sections.append(message_section)

        card["sections"] = sections

        try:
            # Teams Webhookにカードを送信
            response = requests.post(
                self.webhook_url,
                data=json.dumps(card),
                headers={"Content-Type": "application/json"},
            )

            # レスポンスの確認
            response.raise_for_status()
            return True

        except requests.RequestException as e:
            print(f"Microsoft Teamsメッセージ送信中にエラーが発生しました: {e}")
            return False

    def send_error_message(
        self, error_message: str, error_details: Optional[str] = None, **kwargs
    ) -> bool:
        """
        エラー通知用のメッセージをTeamsに送信する

        Args:
            error_message (str): エラーの概要
            error_details (Optional[str]): エラーの詳細情報
            **kwargs: その他の引数

        Returns:
            bool: メッセージ送信の成否
        """
        message = error_message
        if error_details:
            message += f"\n\n**詳細情報**:\n{error_details}"

        return self.send_message(
            message=message,
            title="エラーが発生しました",
            theme_color="FF0000",  # 赤色
            **kwargs,
        )

    def send_success_message(
        self, success_message: str, additional_info: Optional[str] = None, **kwargs
    ) -> bool:
        """
        成功通知用のメッセージをTeamsに送信する

        Args:
            success_message (str): 成功の概要
            additional_info (Optional[str]): 追加情報
            **kwargs: その他の引数

        Returns:
            bool: メッセージ送信の成否
        """
        message = success_message
        if additional_info:
            message += f"\n\n**追加情報**:\n{additional_info}"

        return self.send_message(
            message=message,
            title="処理が成功しました",
            theme_color="00FF00",  # 緑色
            **kwargs,
        )
