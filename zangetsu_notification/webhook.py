import json
import os
from typing import Any, Dict, Optional

import requests

from zangetsu_notification.base import NotificationBase


class WebhookNotification(NotificationBase):
    """
    カスタムWebhookに通知を送信するユーティリティクラス

    任意のWebhookエンドポイントにJSON形式でデータを送信します。
    社内システムやサードパーティツールとの連携に使用できます。
    """

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        default_payload: Optional[Dict[str, Any]] = None,
    ):
        """
        Webhook通知クラスの初期化

        Args:
            webhook_url (Optional[str]): WebhookのURL
                指定しない場合は環境変数から取得
            headers (Optional[Dict[str, str]]): リクエストヘッダー
            default_payload (Optional[Dict[str, Any]]): デフォルトのペイロード

        Raises:
            ValueError: Webhook URLが見つからない場合
        """
        super().__init__()

        # webhook_urlが指定されていない場合は環境変数から取得
        if webhook_url is None:
            webhook_url = os.getenv("WEBHOOK_URL")

        if not webhook_url:
            raise ValueError(
                "Webhook URLが指定されていません。"
                "環境変数WEBHOOK_URLを設定するか、"
                "コンストラクタに直接URLを渡してください。"
            )

        self.webhook_url = webhook_url
        self.headers = headers or {"Content-Type": "application/json"}
        self.default_payload = default_payload or {}

    def send_message(
        self, message: str, payload: Optional[Dict[str, Any]] = None, **kwargs
    ) -> bool:
        """
        Webhookにメッセージを送信する

        Args:
            message (str): 送信するメッセージ本文
            payload (Optional[Dict[str, Any]]): 送信するペイロード
            **kwargs: ペイロードに追加する追加のキーワード引数

        Returns:
            bool: メッセージ送信の成否
        """
        # ベースとなるペイロードを準備
        webhook_payload = self.default_payload.copy()

        # カスタムペイロードがあれば追加
        if payload:
            webhook_payload.update(payload)

        # メッセージを追加
        webhook_payload["message"] = message

        # その他のキーワード引数があれば追加
        if kwargs:
            for key, value in kwargs.items():
                if key not in webhook_payload:
                    webhook_payload[key] = value

        try:
            # Webhookにリクエスト送信
            response = requests.post(
                self.webhook_url, headers=self.headers, data=json.dumps(webhook_payload)
            )

            # レスポンスの確認
            response.raise_for_status()
            return True

        except requests.RequestException as e:
            print(f"Webhookメッセージ送信中にエラーが発生しました: {e}")
            return False

    def send_error_message(
        self, error_message: str, error_details: Optional[str] = None, **kwargs
    ) -> bool:
        """
        エラー通知用のメッセージをWebhookに送信する

        Args:
            error_message (str): エラーの概要
            error_details (Optional[str]): エラーの詳細情報
            **kwargs: 追加のキーワード引数

        Returns:
            bool: メッセージ送信の成否
        """
        # エラー用のペイロード
        error_payload = {
            "type": "error",
            "title": "エラーが発生しました",
            "message": error_message,
        }

        # エラー詳細がある場合は追加
        if error_details:
            error_payload["details"] = error_details

        return self.send_message(message=error_message, payload=error_payload, **kwargs)

    def send_success_message(
        self, success_message: str, additional_info: Optional[str] = None, **kwargs
    ) -> bool:
        """
        成功通知用のメッセージをWebhookに送信する

        Args:
            success_message (str): 成功の概要
            additional_info (Optional[str]): 追加情報
            **kwargs: 追加のキーワード引数

        Returns:
            bool: メッセージ送信の成否
        """
        # 成功用のペイロード
        success_payload = {
            "type": "success",
            "title": "処理が成功しました",
            "message": success_message,
        }

        # 追加情報がある場合は追加
        if additional_info:
            success_payload["details"] = additional_info

        return self.send_message(
            message=success_message, payload=success_payload, **kwargs
        )
