import unittest

from zangetsu_notification.base import NotificationBase


class ConcreteNotification(NotificationBase):
    """テスト用の具象クラス"""

    def send_message(self, message, **kwargs):
        return True

    def send_error_message(self, error_message, error_details=None, **kwargs):
        return True

    def send_success_message(self, success_message, additional_info=None, **kwargs):
        return True


class TestNotificationBase(unittest.TestCase):
    """NotificationBaseクラスのテスト"""

    def test_abstract_methods(self):
        """抽象メソッドが正しく実装されているか確認"""
        # インスタンス化できることを確認
        notifier = ConcreteNotification()

        # メソッドが実装されていることを確認
        self.assertTrue(hasattr(notifier, "send_message"))
        self.assertTrue(hasattr(notifier, "send_error_message"))
        self.assertTrue(hasattr(notifier, "send_success_message"))

        # 各メソッドが正しく動作することを確認
        self.assertTrue(notifier.send_message("テストメッセージ"))
        self.assertTrue(notifier.send_error_message("エラーメッセージ"))
        self.assertTrue(notifier.send_success_message("成功メッセージ"))

    def test_abstract_class_cant_instantiate(self):
        """抽象クラスは直接インスタンス化できないことを確認"""
        with self.assertRaises(TypeError):
            NotificationBase()


if __name__ == "__main__":
    unittest.main()
