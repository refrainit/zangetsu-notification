import os
from typing import Any, Dict, List, Optional, Union

from zangetsu_notification.base import NotificationBase
from zangetsu_notification.email import EmailNotification
from zangetsu_notification.line import LineNotification
from zangetsu_notification.slack import SlackNotification
from zangetsu_notification.teams import TeamsNotification
from zangetsu_notification.webhook import WebhookNotification


class NotificationFactory:
    """
    通知クラスのファクトリー

    設定に基づいて適切な通知クラスのインスタンスを生成します。
    """

    @staticmethod
    def create(
        notification_type: str, config: Optional[Dict[str, Any]] = None
    ) -> NotificationBase:
        """
        通知タイプと設定に基づいて通知クラスのインスタンスを作成する

        Args:
            notification_type (str): 通知タイプ
                'slack', 'teams', 'email', 'line', 'webhook'のいずれか
            config (Optional[Dict[str, Any]]): 通知設定

        Returns:
            NotificationBase: 通知クラスのインスタンス

        Raises:
            ValueError: サポートされていない通知タイプの場合
        """
        config = config or {}

        if notification_type.lower() == "slack":
            return SlackNotification(**config)

        elif notification_type.lower() == "teams":
            return TeamsNotification(**config)

        elif notification_type.lower() == "email":
            return EmailNotification(**config)

        elif notification_type.lower() == "line":
            return LineNotification(**config)

        elif notification_type.lower() == "webhook":
            return WebhookNotification(**config)

        else:
            raise ValueError(f"サポートされていない通知タイプです: {notification_type}")

    @staticmethod
    def create_multi(
        notification_types: List[str],
        configs: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> List[NotificationBase]:
        """
        複数の通知クラスのインスタンスを作成する

        Args:
            notification_types (List[str]): 通知タイプのリスト
            configs (Optional[Dict[str, Dict[str, Any]]]): タイプごとの設定

        Returns:
            List[NotificationBase]: 通知クラスのインスタンスリスト
        """
        configs = configs or {}
        notifiers = []

        for notification_type in notification_types:
            config = configs.get(notification_type, {})
            try:
                notifier = NotificationFactory.create(notification_type, config)
                notifiers.append(notifier)
            except Exception as e:
                print(f"{notification_type}通知の初期化中にエラーが発生しました: {e}")

        return notifiers


class MultiNotifier(NotificationBase):
    """
    複数の通知先に同時に通知を送信するクラス
    """

    def __init__(self, notifiers: List[NotificationBase]):
        """
        複数通知クラスの初期化

        Args:
            notifiers (List[NotificationBase]): 通知クラスのインスタンスリスト
        """
        super().__init__()
        self.notifiers = notifiers

    def send_message(self, message: str, **kwargs) -> bool:
        """
        すべての通知先にメッセージを送信する

        Args:
            message (str): 送信するメッセージ本文
            **kwargs: 各通知クラスに渡す追加のパラメータ

        Returns:
            bool: すべての通知が成功したかどうか
        """
        results = []
        for notifier in self.notifiers:
            try:
                # メッセージを最初の位置引数として渡し、残りはキーワード引数
                result = notifier.send_message(message=message, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"通知の送信中にエラーが発生しました: {e}")
                results.append(False)

        # すべての通知が成功した場合のみTrue
        return all(results)

    def send_error_message(
        self, error_message: str, error_details: Optional[str] = None, **kwargs
    ) -> bool:
        """
        すべての通知先にエラーメッセージを送信する

        Args:
            error_message (str): エラーの概要
            error_details (Optional[str]): エラーの詳細情報
            **kwargs: 各通知クラスに渡す追加のパラメータ

        Returns:
            bool: すべての通知が成功したかどうか
        """
        results = []
        for notifier in self.notifiers:
            try:
                # 引数をキーワード引数として明示的に渡す
                result = notifier.send_error_message(
                    error_message=error_message, error_details=error_details, **kwargs
                )
                results.append(result)
            except Exception as e:
                print(f"エラー通知の送信中にエラーが発生しました: {e}")
                results.append(False)

        return all(results)

    def send_success_message(
        self, success_message: str, additional_info: Optional[str] = None, **kwargs
    ) -> bool:
        """
        すべての通知先に成功メッセージを送信する

        Args:
            success_message (str): 成功の概要
            additional_info (Optional[str]): 追加情報
            **kwargs: 各通知クラスに渡す追加のパラメータ

        Returns:
            bool: すべての通知が成功したかどうか
        """
        results = []
        for notifier in self.notifiers:
            try:
                # 引数をキーワード引数として明示的に渡す
                result = notifier.send_success_message(
                    success_message=success_message,
                    additional_info=additional_info,
                    **kwargs,
                )
                results.append(result)
            except Exception as e:
                print(f"成功通知の送信中にエラーが発生しました: {e}")
                results.append(False)

        return all(results)


def create_notifier(
    notification_type: Union[str, List[str]], config: Optional[Dict[str, Any]] = None
) -> NotificationBase:
    """
    通知インスタンスを作成するヘルパー関数

    Args:
        notification_type (Union[str, List[str]]): 通知タイプまたは通知タイプのリスト
        config (Optional[Dict[str, Any]]): 通知設定

    Returns:
        NotificationBase: 単一または複数の通知クラスのインスタンス
    """
    if isinstance(notification_type, list):
        # 複数の通知タイプが指定された場合
        configs = {}
        if config:
            for type_name in notification_type:
                type_config = config.get(type_name, {})
                configs[type_name] = type_config

        notifiers = NotificationFactory.create_multi(notification_type, configs)
        return MultiNotifier(notifiers)
    else:
        # 単一の通知タイプが指定された場合
        return NotificationFactory.create(notification_type, config)


def from_env() -> NotificationBase:
    """
    環境変数から通知設定を読み取り、適切な通知インスタンスを作成する

    環境変数:
        NOTIFICATION_TYPE: 通知タイプ（カンマ区切りで複数指定可）

    Returns:
        NotificationBase: 通知クラスのインスタンス
    """
    notification_types_env = os.getenv("NOTIFICATION_TYPE", "slack")
    notification_types = [t.strip() for t in notification_types_env.split(",")]

    if len(notification_types) == 1:
        return create_notifier(notification_types[0])
    else:
        return create_notifier(notification_types)
