import os
from typing import Optional

import requests

from zangetsu_notification.base import NotificationBase


class LineNotification(NotificationBase):
    """
    LINE Notifyを使用して通知を送信するユーティリティクラス

    LINEグループやユーザーへのメッセージ送信を行います。
    """

    # LINE Notify API URL
    API_URL = "https://notify-api.line.me/api/notify"

    def __init__(self, access_token: Optional[str] = None):
        """
        LINE Notify通知クラスの初期化

        Args:
            access_token (Optional[str]): LINE Notifyのアクセストークン
                指定しない場合は環境変数から取得

        Raises:
            ValueError: アクセストークンが見つからない場合
        """
        super().__init__()

        # アクセストークンが指定されていない場合は環境変数から取得
        if access_token is None:
            access_token = os.getenv("LINE_NOTIFY_TOKEN")

        if not access_token:
            raise ValueError(
                "LINE Notifyアクセストークンが指定されていません。"
                "環境変数LINE_NOTIFY_TOKENを設定するか、"
                "コンストラクタに直接トークンを渡してください。"
            )

        self.access_token = access_token

    def send_message(
        self,
        message: str,
        image_url: Optional[str] = None,
        image_thumbnail: Optional[str] = None,
        sticker_package_id: Optional[int] = None,
        sticker_id: Optional[int] = None,
        **kwargs,
    ) -> bool:
        """
        LINE Notifyにメッセージを送信する

        Args:
            message (str): 送信するメッセージ本文
            image_url (Optional[str]): 送信する画像のURL
            image_thumbnail (Optional[str]): 送信する画像のサムネイルURL
            sticker_package_id (Optional[int]): スタンプのパッケージID
            sticker_id (Optional[int]): スタンプID
            **kwargs: その他の引数

        Returns:
            bool: メッセージ送信の成否
        """
        # ヘッダーにアクセストークンを設定
        headers = {"Authorization": f"Bearer {self.access_token}"}

        # パラメータを設定
        payload = {"message": message}

        # 画像URLが指定されている場合
        if image_url:
            payload["imageFullsize"] = image_url
            if image_thumbnail:
                payload["imageThumbnail"] = image_thumbnail
            else:
                payload["imageThumbnail"] = image_url

        # スタンプが指定されている場合
        if sticker_package_id and sticker_id:
            payload["stickerPackageId"] = sticker_package_id
            payload["stickerId"] = sticker_id

        try:
            # LINE Notify APIにリクエスト送信
            response = requests.post(self.API_URL, headers=headers, data=payload)

            # レスポンスの確認
            response.raise_for_status()
            return True

        except requests.RequestException as e:
            print(f"LINE Notifyメッセージ送信中にエラーが発生しました: {e}")
            return False

    def send_error_message(
        self, error_message: str, error_details: Optional[str] = None, **kwargs
    ) -> bool:
        """
        エラー通知用のメッセージをLINE Notifyに送信する

        Args:
            error_message (str): エラーの概要
            error_details (Optional[str]): エラーの詳細情報
            **kwargs: その他の引数

        Returns:
            bool: メッセージ送信の成否
        """
        # エラーアイコン絵文字
        error_icon = "\u26a0"  # ⚠ 警告マーク

        # エラーメッセージの作成
        message = f"{error_icon} エラーが発生しました {error_icon}\n{error_message}"

        # エラー詳細がある場合は追加
        if error_details:
            message += f"\n\n【詳細情報】\n{error_details}"

        return self.send_message(message=message, **kwargs)

    def send_success_message(
        self, success_message: str, additional_info: Optional[str] = None, **kwargs
    ) -> bool:
        """
        成功通知用のメッセージをLINE Notifyに送信する

        Args:
            success_message (str): 成功の概要
            additional_info (Optional[str]): 追加情報
            **kwargs: その他の引数

        Returns:
            bool: メッセージ送信の成否
        """
        # 成功アイコン絵文字
        success_icon = "\u2705"  # ✅ チェックマーク

        # 成功メッセージの作成
        message = f"{success_icon} 処理が成功しました {success_icon}\n{success_message}"

        # 追加情報がある場合は追加
        if additional_info:
            message += f"\n\n【追加情報】\n{additional_info}"

        return self.send_message(message=message, **kwargs)
