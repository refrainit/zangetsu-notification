# zangetsu-notification

多様な通知メカニズムをシンプルなインターフェースで提供する通知ライブラリです。

## 特徴

- **多様な通知先サポート**：Slack、Microsoft Teams、Email、LINE Notify、カスタム Webhook など
- **統一インターフェース**：すべての通知先で一貫したメソッド呼び出し
- **複数チャネル対応**：1 回の操作で複数の通知先に同時送信
- **エラー耐性**：一部の通知先が失敗しても処理を継続
- **環境変数サポート**：設定の外部化が容易
- **拡張性**：新しい通知先を追加する仕組みを提供
- **柔軟な設定**：コード内での設定と環境変数による設定の両方をサポート

## インストール

```bash
pip install zangetsu-notification
```

## 基本的な使い方

### Slack 通知

```python
from zangetsu_notification import SlackNotification

# 環境変数 SLACK_WEBHOOK_URL を使用する場合
slack = SlackNotification()

# または直接Webhook URLを指定
slack = SlackNotification(webhook_url="https://hooks.slack.com/services/XXX/YYY/ZZZ")

# 基本的なメッセージ送信
slack.send_message("テスト通知です", username="通知ボット", icon_emoji=":bell:")

# エラー通知
slack.send_error_message(
    "バッチ処理エラー",
    "データ処理中にタイムアウトが発生しました"
)

# 成功通知
slack.send_success_message(
    "バッチ処理完了",
    "100件のデータを正常に処理しました"
)
```

### Microsoft Teams 通知

```python
from zangetsu_notification import TeamsNotification

# 環境変数 TEAMS_WEBHOOK_URL を使用する場合
teams = TeamsNotification()

# またはURLを直接指定
teams = TeamsNotification(webhook_url="https://outlook.office.com/webhook/XXX/YYY/ZZZ")

# 基本的なメッセージ送信
teams.send_message(
    "テスト通知です",
    title="通知タイトル",
    subtitle="詳細情報"
)

# エラー通知（赤色のカード）
teams.send_error_message("API接続エラー", "認証情報が無効です")

# 成功通知（緑色のカード）
teams.send_success_message("デプロイ完了", "アプリケーションがデプロイされました")
```

### メール通知

```python
from zangetsu_notification import EmailNotification

# SMTP設定を直接指定
email = EmailNotification(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    smtp_username="your-email@gmail.com",
    smtp_password="your-app-password",
    sender_email="your-email@gmail.com"
)

# 基本的なメール送信
email.send_message(
    message="テストメッセージ本文",
    subject="テスト通知",
    recipients=["recipient@example.com"],
    cc=["cc-recipient@example.com"],
    html_message="<p>HTMLフォーマットの<strong>メッセージ</strong></p>"
)

# エラー通知メール
email.send_error_message(
    "バックアップエラー",
    "バックアップ処理中にディスク容量不足が発生しました",
    recipients=["admin@example.com"]
)
```

### LINE Notify 通知

```python
from zangetsu_notification import LineNotification

# 環境変数 LINE_NOTIFY_TOKEN を使用する場合
line = LineNotification()

# またはトークンを直接指定
line = LineNotification(access_token="YOUR_LINE_NOTIFY_TOKEN")

# 基本的なメッセージ送信
line.send_message("テスト通知です")

# 画像付きメッセージ
line.send_message(
    "画像付きメッセージ",
    image_url="https://example.com/image.jpg"
)

# エラー通知
line.send_error_message("システムエラー", "サーバー接続が切断されました")
```

### Webhook 通知

```python
from zangetsu_notification import WebhookNotification

# Webhook URL設定
webhook = WebhookNotification(
    webhook_url="https://example.com/api/webhook",
    headers={"Authorization": "Bearer token123"}
)

# 基本的なメッセージ送信
webhook.send_message(
    "テスト通知です",
    payload={
        "severity": "info",
        "source": "batch_process"
    }
)

# エラー通知
webhook.send_error_message(
    "データベースエラー",
    "クエリのタイムアウトが発生しました"
)
```

## 複数通知先への同時送信

```python
from zangetsu_notification import create_notifier

# 複数通知先の設定
notifier = create_notifier(
    ["slack", "email"],  # 通知タイプのリスト
    {
        "slack": {
            "webhook_url": "https://hooks.slack.com/services/XXX/YYY/ZZZ"
        },
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "your-email@gmail.com",
            "smtp_password": "your-password",
            "sender_email": "your-email@gmail.com"
        }
    }
)

# 両方の通知先に一度に送信
notifier.send_message("重要な更新があります")
notifier.send_error_message("緊急エラー", "システムがダウンしています")
notifier.send_success_message("デプロイ成功", "新バージョンがデプロイされました")
```

## 環境変数から自動設定

```python
from zangetsu_notification import from_env

# 環境変数の設定例
# export NOTIFICATION_TYPE=slack,line
# export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
# export LINE_NOTIFY_TOKEN=your-line-token

# 環境変数から通知設定を自動的に読み込み
notifier = from_env()

# 設定されたすべての通知先に送信
notifier.send_message("環境変数から設定された通知です")
```

## 環境変数リファレンス

各通知先では以下の環境変数がサポートされています：

| 通知先  | 環境変数                   | 説明                                                     |
| ------- | -------------------------- | -------------------------------------------------------- |
| 全般    | `NOTIFICATION_TYPE`        | カンマ区切りの通知タイプリスト（例: `slack,email,line`） |
| Slack   | `SLACK_WEBHOOK_URL`        | Slack の Webhook URL                                     |
| Teams   | `TEAMS_WEBHOOK_URL`        | Microsoft Teams の Webhook URL                           |
| Email   | `SMTP_SERVER`              | SMTP サーバーアドレス                                    |
| Email   | `SMTP_PORT`                | SMTP ポート（デフォルト: 587）                           |
| Email   | `SMTP_USERNAME`            | SMTP ユーザー名                                          |
| Email   | `SMTP_PASSWORD`            | SMTP パスワード                                          |
| Email   | `SENDER_EMAIL`             | 送信元メールアドレス                                     |
| Email   | `DEFAULT_EMAIL_RECIPIENTS` | デフォルトの受信者（カンマ区切り）                       |
| LINE    | `LINE_NOTIFY_TOKEN`        | LINE Notify アクセストークン N                           |
| Webhook | `WEBHOOK_URL`              | カスタム Webhook URL                                     |

## 拡張

新しい通知先を追加するには、`NotificationBase`クラスを継承して必要なメソッドを実装します：

```python
from zangetsu_notification.base import NotificationBase

class MyCustomNotification(NotificationBase):
    """カスタム通知クラス"""

    def __init__(self, api_key=None):
        super().__init__()
        self.api_key = api_key or os.getenv("MY_SERVICE_API_KEY")
        # 初期化処理

    def send_message(self, message, **kwargs):
        # メッセージ送信の実装
        return True

    def send_error_message(self, error_message, error_details=None, **kwargs):
        # エラーメッセージ送信の実装
        return True

    def send_success_message(self, success_message, additional_info=None, **kwargs):
        # 成功メッセージ送信の実装
        return True
```

## 貢献

1. リポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## ライセンス

[社内ライセンス名] - 詳細は LICENSE ファイルを参照してください。

## 依存関係

- Python 3.9+
- requests

## トラブルシューティング

- **Slack 通知が送信されない**: Webhook URL が正しいことと、アプリがチャンネルに追加されていることを確認してください
- **メール送信エラー**: SMTP 設定を確認し、Gmail の場合はアプリパスワードを使用してください
- **LINE 通知エラー**: トークンの有効期限が切れていないか確認してください
