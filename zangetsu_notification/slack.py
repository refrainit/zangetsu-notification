import json
import os
from typing import Any, Dict, List, Optional

import requests

from zangetsu_notification.base import NotificationBase


class SlackNotification(NotificationBase):
    """
    Slackに通知を送信するユーティリティクラス

    環境変数やコンフィグからWebhook URLを取得し、
    メッセージ送信を可能にします。
    """

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Slackノティフィケーションクラスの初期化

        Args:
            webhook_url (Optional[str]): Slackのwebhook URL。
                指定しない場合は環境変数から取得を試みます。

        Raises:
            ValueError: Webhook URLが見つからない場合
        """
        super().__init__()

        # webhook_urlが指定されていない場合は環境変数から取得
        if webhook_url is None:
            webhook_url = os.getenv("SLACK_WEBHOOK_URL")

        if not webhook_url:
            raise ValueError(
                "Slack Webhook URLが指定されていません。"
                "環境変数SLACK_WEBHOOK_URLを設定するか、"
                "コンストラクタに直接URLを渡してください。"
            )

        self.webhook_url = webhook_url

    def _format_mention(self, mention: str) -> str:
        """
        メンション文字列を適切な形式に変換する

        Args:
            mention (str): メンション文字列
            - 名前: 'Makoto Horikawa'
            - ユーザーID: 'U012345678'
            - メールアドレス: 'makoto.horikawa@example.com'

        Returns:
            str: フォーマットされたSlackメンション文字列
        """
        # すでに正しいSlackメンション形式の場合はそのまま返す
        if mention.startswith("<@") and mention.endswith(">"):
            return mention

        # ユーザーIDの場合
        if mention.startswith("U") and len(mention) > 8:
            return f"<@{mention}>"

        # メールアドレスの場合は変換できないため、そのまま返す
        if "@" in mention and "." in mention:
            return mention

        # デフォルトは名前から変換を試みる
        # 名前からユーザーIDを取得する方法が必要
        # 現状では、実際のユーザーIDに変換する処理が必要
        return mention

    def send_message(
        self,
        message: str,
        username: str = "Notification Bot",
        icon_emoji: str = ":bell:",
        channel: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        mentions: Optional[List[str]] = None,
        **kwargs,
    ) -> bool:
        """
        Slackにメッセージを送信する

        Args:
            message (str): 送信するメッセージ本文
            username (str): 送信者の表示名。デフォルトは'Notification Bot'
            icon_emoji (str): ボットのアイコン絵文字。デフォルトは':bell:'
            channel (Optional[str]): 送信先チャンネル
            attachments (Optional[List[Dict[str, Any]]]): メッセージに追加する添付情報
            mentions (Optional[List[str]]): メンションするユーザー
            **kwargs: その他の引数（互換性のため）

        Returns:
            bool: メッセージ送信の成否
        """
        # メンション処理
        if mentions:
            # 各メンションを適切な形式に変換
            mention_text = " ".join(self._format_mention(m) for m in mentions)
            message = f"{mention_text}\n{message}"

        # メッセージペイロードの作成
        payload: Dict[str, Any] = {
            "text": message,
            "username": username,
            "icon_emoji": icon_emoji,
        }

        # チャンネルが指定されている場合
        if channel:
            payload["channel"] = channel

        # 添付情報がある場合
        if attachments:
            payload["attachments"] = attachments

        try:
            # メッセージ送信
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            )

            # レスポンスの確認
            response.raise_for_status()
            return True

        except requests.RequestException as e:
            print(f"Slackメッセージ送信中にエラーが発生しました: {e}")
            return False

    def send_error_message(
        self,
        error_message: str,
        error_details: Optional[str] = None,
        username: str = "Error Bot",
        icon_emoji: str = ":warning:",
        mentions: Optional[List[str]] = None,
        **kwargs,
    ) -> bool:
        """
        エラー通知用のメッセージを送信する

        Args:
            error_message (str): エラーの概要
            error_details (Optional[str]): エラーの詳細情報
            username (str): 送信者の表示名
            icon_emoji (str): アイコン絵文字
            mentions (Optional[List[str]]): メンションするユーザー
            **kwargs: その他の引数（互換性のため）

        Returns:
            bool: メッセージ送信の成否
        """
        # エラー通知用の添付情報を作成
        attachments = [
            {
                "color": "danger",
                "title": "エラー詳細",
                "text": error_details or "エラーの詳細情報はありません。",
            }
        ]

        return self.send_message(
            message=f"*エラーが発生しました*: {error_message}",
            username=username,
            icon_emoji=icon_emoji,
            attachments=attachments,
            mentions=mentions,
        )

    def send_success_message(
        self,
        success_message: str,
        additional_info: Optional[str] = None,
        username: str = "Success Bot",
        icon_emoji: str = ":white_check_mark:",
        mentions: Optional[List[str]] = None,
        **kwargs,
    ) -> bool:
        """
        成功通知用のメッセージを送信する

        Args:
            success_message (str): 成功の概要
            additional_info (Optional[str]): 追加情報
            username (str): 送信者の表示名
            icon_emoji (str): アイコン絵文字
            mentions (Optional[List[str]]): メンションするユーザー
            **kwargs: その他の引数（互換性のため）

        Returns:
            bool: メッセージ送信の成否
        """
        # 成功通知用の添付情報を作成
        attachments = []
        if additional_info:
            attachments.append(
                {"color": "good", "title": "追加情報", "text": additional_info}
            )

        return self.send_message(
            message=f"*成功*: {success_message}",
            username=username,
            icon_emoji=icon_emoji,
            attachments=attachments,
            mentions=mentions,
        )
