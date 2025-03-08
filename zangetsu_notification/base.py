from abc import ABC, abstractmethod
from typing import Optional


class NotificationBase(ABC):
    """
    通知機能の基底クラス

    異なる通知チャネル（Slack, Teams, Email, LineNotify等）の
    基盤となる共通機能を提供します。
    """

    def __init__(self):
        """通知基底クラスの初期化"""
        pass

    @abstractmethod
    def send_message(self, message: str, **kwargs) -> bool:
        """
        メッセージを送信する

        Args:
            message (str): 送信するメッセージ本文
            **kwargs: 各通知先に固有のパラメータ

        Returns:
            bool: メッセージ送信の成否
        """
        pass

    @abstractmethod
    def send_error_message(
        self, error_message: str, error_details: Optional[str] = None, **kwargs
    ) -> bool:
        """
        エラー通知用のメッセージを送信する

        Args:
            error_message (str): エラーの概要
            error_details (Optional[str]): エラーの詳細情報
            **kwargs: 各通知先に固有のパラメータ

        Returns:
            bool: メッセージ送信の成否
        """
        pass

    @abstractmethod
    def send_success_message(
        self, success_message: str, additional_info: Optional[str] = None, **kwargs
    ) -> bool:
        """
        成功通知用のメッセージを送信する

        Args:
            success_message (str): 成功の概要
            additional_info (Optional[str]): 追加情報
            **kwargs: 各通知先に固有のパラメータ

        Returns:
            bool: メッセージ送信の成否
        """
        pass
