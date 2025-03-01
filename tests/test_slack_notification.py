"""
Slack通知のユニットテスト
"""

import unittest
from unittest.mock import MagicMock, patch

import pytest

from senju3_notification.slack import SlackNotification

class TestSlackNotification(unittest.TestCase):
    """SlackNotificationクラスのテスト"""

    def setUp(self):
        """テスト前の共通セットアップ"""
        pass

    def tearDown(self):
        """テスト後のクリーンアップ"""
        pass
    
    def test_init(self):
        """SlackNotificationの初期化テスト"""
        # 環境変数から取得
        with patch("os.getenv", MagicMock(return_value="https://slack.com/webhook")):
            slack = SlackNotification()
            self.assertEqual(slack.webhook_url, "https://slack.com/webhook")
            
        # 引数で指定
        slack = SlackNotification("https://slack.com/webhook")
        self.assertEqual(slack.webhook_url, "https://slack.com/webhook")
        
    