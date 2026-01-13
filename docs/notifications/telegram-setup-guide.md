# Telegram Notifications Setup Guide

## ⚡ Quick Start (For Users)

**Want to receive alerts?** It takes 30 seconds:

1. **Open Telegram** and search for **@polymarb_alert_bot**
2. **Click "Start"** or send `/start`
3. **Done!** You'll now receive alerts when opportunities are detected

**Test it**:
```bash
curl https://capstone-polymarket-arbitrage-agent-production.up.railway.app/api/telegram/test
```

That's it! No configuration needed. 🎉

---

## Overview

The Polymarket Arbitrage Agent can send real-time notifications to Telegram when arbitrage opportunities are detected. This guide walks you through setting up Telegram bot notifications.

## ✨ New: Multi-Chat Broadcasting

**Good news**: The system now supports **automatic multi-chat broadcasting**! Anyone who starts the bot will receive alerts - no manual configuration needed.

### How It Works

1. **Users subscribe automatically** by sending `/start` to the bot
2. **System tracks all subscribers** in the database
3. **Alerts broadcast to all active subscribers** simultaneously
4. **No configuration required** - just start the bot and you're done!

### Benefits

- ✅ **Anyone can subscribe** - Just start the bot
- ✅ **Unlimited subscribers** - Support for multiple users
- ✅ **Automatic management** - System tracks all subscribers
- ✅ **No manual setup** - No need to configure individual chat IDs

### For Developers

If you're deploying your own instance, see the [Advanced Configuration](#advanced-configuration) section below for setup instructions.

---

## What You'll Get

When Telegram notifications are enabled, you'll receive instant messages in Telegram with:

- 🔴 **CRITICAL** alerts (high-confidence opportunities)
- ⚠️ **WARNING** alerts (medium-confidence opportunities)
- ℹ️ **INFO** alerts (optional, low-confidence opportunities)

Each alert includes:
- Market question and current/expected prices
- News headline and link
- AI reasoning explanation
- Recommended action
- Confidence score

## Prerequisites

- Telegram account (free)
- 5 minutes to set up

## Step-by-Step Setup

### Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Start a chat and send `/newbot`
3. Choose a name for your bot (e.g., "Polymarket Arbitrage Bot")
4. Choose a username for your bot (e.g., `my_polymarket_bot`)
5. **Copy the bot token** (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Example conversation with BotFather**:
```
You: /newbot
BotFather: Alright, a new bot. How are we going to call it? Please choose a name for your bot.
You: Polymarket Arbitrage Bot
BotFather: Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.
You: polymarket_arbitrage_bot
BotFather: Done! Congratulations on your new bot. You will find it at t.me/polymarket_arbitrage_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands.

Use this token to access the HTTP API:
123456789:ABCdefGHIjklMNOpqrsTUVwxyz

Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

### Step 2: Get Your Chat ID

**Option A: Via Direct Message (Recommended)**

1. Find your bot in Telegram (search for the username you chose)
2. Start a chat with your bot
3. Send `/start` to your bot
4. Visit this URL in your browser (replace `YOUR_BOT_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
5. Look for `"chat":{"id":123456789}` in the response
6. Copy that number (your chat ID)

**Example response**:
```json
{
  "ok": true,
  "result": [
    {
      "update_id": 123456789,
      "message": {
        "message_id": 1,
        "from": {
          "id": 987654321,
          "is_bot": false,
          "first_name": "Your Name"
        },
        "chat": {
          "id": 987654321,
          "first_name": "Your Name",
          "type": "private"
        },
        "date": 1704067200,
        "text": "/start"
      }
    }
  ]
}
```
Your chat ID is `987654321`.

**Option B: Via a Group/Channel**

1. Add your bot to the group/channel
2. Send a message in the group/channel
3. Visit `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
4. Find your group/channel's chat ID (usually negative for groups)
5. Copy that number

### Step 3: Configure Environment Variables

Add the following to your `.env` file:

```bash
# Telegram Notifications
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
TELEGRAM_ENABLED=true
TELEGRAM_MIN_SEVERITY=WARNING
```

**Configuration Options**:

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | `123456:ABC...` | Yes |
| `TELEGRAM_CHAT_ID` | Your chat ID | `987654321` | Yes |
| `TELEGRAM_ENABLED` | Enable/disable notifications | `true` or `false` | No (default: true) |
| `TELEGRAM_MIN_SEVERITY` | Minimum severity to notify | `INFO`, `WARNING`, or `CRITICAL` | No (default: WARNING) |

### Step 4: Test Your Configuration

#### Test via Python Script

Create a test script `test_telegram.py`:

```python
from src.notifications.telegram_notifier import create_telegram_notifier
from src.models.alert import AlertSeverity

# Create notifier
notifier = create_telegram_notifier(
    bot_token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID",
    enabled=True,
    min_severity=AlertSeverity.INFO
)

# Send test message
if notifier.send_test_message():
    print("✅ Telegram test successful!")
else:
    print("❌ Telegram test failed!")
```

Run it:
```bash
python test_telegram.py
```

You should receive a test message in Telegram.

#### Test via Railway Deployment

If using Railway, set the environment variables in the Railway dashboard:

1. Go to Railway Dashboard → Your Project
2. Click on **Variables** tab
3. Add the Telegram variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `TELEGRAM_ENABLED` = `true`
   - `TELEGRAM_MIN_SEVERITY` = `WARNING`
4. Redeploy the service

After deployment, your bot will send a test message automatically on startup.

### Step 5: Start Receiving Alerts

Once configured, you'll automatically receive Telegram notifications when:

- **CRITICAL opportunities** are detected (high confidence, high profit potential)
- **WARNING opportunities** are detected (medium confidence or profit potential)
- **INFO opportunities** are detected (if `TELEGRAM_MIN_SEVERITY=INFO`)

## Example Alert Message

```
🔴 *CRITICAL: Market Price Discrepancy Detected*

*Severity:* CRITICAL
*Confidence:* 85.3%

💼 *Market:*
Will Bitcoin exceed $100,000 by June 2025?

*Current Price:* 0.3500
*Expected Price:* 0.6500
*Discrepancy:* 85.71%

📰 *News:*
[SEC approves Bitcoin ETF for trading](https://example.com/news/article)

🧠 *Reasoning:*
Breaking news: SEC has officially approved Bitcoin ETF applications. This is a major regulatory milestone that will significantly increase institutional accessibility and demand. The market price of 35¢ does not reflect this new information...

🎯 *Recommended Action:* Buy YES tokens

_Alert ID: abc123-def456-ghi789_
```

## Managing Subscribers

The system automatically tracks anyone who starts the bot, but you can also manage subscribers programmatically via the API.

### View All Subscribers

```bash
curl https://your-app.up.railway.app/api/telegram/subscribers
```

Response:
```json
[
  {
    "chat_id": "123456789",
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "subscribed_at": "2026-01-13T10:00:00",
    "is_active": true
  }
]
```

### Get Subscriber Count

```bash
curl https://your-app.up.railway.app/api/telegram/status
```

Response:
```json
{
  "enabled": true,
  "configured": true,
  "min_severity": "WARNING",
  "chat_id": "123456789",
  "total_subscribers": 5
}
```

### Add Subscriber Manually

```bash
curl -X POST https://your-app.up.railway.app/api/telegram/subscribers/CHAT_ID
```

**Use case**: Add subscribers who haven't started the bot yet, or add groups/channels.

### Remove Subscriber

```bash
curl -X DELETE https://your-app.up.railway.app/api/telegram/subscribers/CHAT_ID
```

**Use case**: Unsubscribe users who no longer want alerts (soft delete - they can re-subscribe by starting the bot again).

### Send Test Broadcast

```bash
curl https://your-app.up.railway.app/api/telegram/test
```

**Use case**: Verify Telegram notifications are working for all subscribers.

---

## Troubleshooting

### Bot not sending messages?

**1. Verify bot token is correct**:
- Visit `https://api.telegram.org/botYOUR_TOKEN/getMe`
- Should return bot info
- If error, token is invalid

**2. Verify chat ID is correct**:
- Send a message to your bot
- Visit `https://api.telegram.org/botYOUR_TOKEN/getUpdates`
- Find the chat ID in the response

**3. Check bot has permission to message you**:
- You must have started a chat with the bot (send `/start`)
- For groups, bot must be added to the group

**4. Check logs**:
```bash
# Local development
tail -f logs/arbitrage_agent.log | grep telegram

# Railway deployment
railway logs --tail | grep telegram
```

### Not receiving all alerts?

**Check minimum severity setting**:
- If `TELEGRAM_MIN_SEVERITY=CRITICAL`, you won't receive WARNING or INFO alerts
- Set to `WARNING` for most alerts
- Set to `INFO` for all alerts (may be noisy)

### Want to disable Telegram temporarily?

Set `TELEGRAM_ENABLED=false` in your environment variables and restart. The bot won't send notifications but will keep running.

## Advanced Configuration

### Multiple Chat IDs

To send alerts to multiple chats/channels, modify the notifier:

```python
chat_ids = ["987654321", "-1001234567890"]  # Personal + group

for chat_id in chat_ids:
    notifier = create_telegram_notifier(
        bot_token="YOUR_TOKEN",
        chat_id=chat_id
    )
    notifier.send_alert(alert)
```

### Custom Message Formatting

Edit `src/notifications/telegram_notifier.py` and modify the `_format_alert` method to customize message appearance.

### Rate Limiting

Telegram has rate limits:
- No more than 30 messages per second to a single chat
- No more than 20 messages per minute to a group

The system includes automatic rate limiting. If you have many alerts, consider:
- Increasing `TELEGRAM_MIN_SEVERITY` to `CRITICAL`
- Setting `alert_cooldown` in configuration

## Security Best Practices

### ✅ DO:
- Store bot tokens in environment variables
- Never commit tokens to Git
- Use `.env.example` with placeholder values
- Regenerate tokens if accidentally exposed

### ❌ DON'T:
- Share bot tokens publicly
- Commit tokens to version control
- Use the same bot for multiple applications
- Give bot unnecessary permissions

## Railway Deployment Specifics

When deploying to Railway:

1. **Add Variables in Railway Dashboard** (not in .env file):
   - Railway → Your Project → Variables
   - Add `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, etc.

2. **Redeploy after adding variables**:
   - Variables are only loaded on deployment/restart
   - Click "New Deployment" after adding variables

3. **Test in production**:
   - Check logs: `railway logs --tail`
   - Look for `telegram_notifications_enabled` message

## Next Steps

- ✅ Telegram notifications configured
- ✅ Receiving real-time alerts
- 📊 Monitor alert quality and adjust `TELEGRAM_MIN_SEVERITY` if needed
- 🔔 Consider setting up additional notification channels (email, Slack, etc.)

## Need Help?

- **Telegram Bot API docs**: https://core.telegram.org/bots/api
- **BotFather commands**: Send `/help` to @BotFather
- **Project issues**: Check GitHub Issues or create a new one

---

**Last Updated**: 2026-01-13
**Status**: ✅ Production Ready
