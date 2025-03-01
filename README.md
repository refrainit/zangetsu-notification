# senju-notification
通知機能ライブラリ

## 使い方

### インストール

```bash
pip install git+https://github.com/leadingtechdev/senju-notification.git
```

### 通知先の設定

環境変数`SLACK_WEBHOOK_URL`にSlackのWebhook URLを設定してください。

- [SlackのWebhook URLの取得](https://api.slack.com/apps/A08EVSK0AES/incoming-webhooks?)

### 通知の送信例

```python
from senju3_notification import SlackNotification

def main():
    slack = SlackNotification()
    slack.send_message("Hello, World!")  # メッセージの送信
    slack.send_success_message("Success", "This is a success message.")  # 成功メッセージの送信
    slack.send_error_message("Error", "This is an error message.")  # エラーメッセージの送信

if __name__ == "__main__":
    main()

```