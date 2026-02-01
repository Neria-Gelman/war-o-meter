# War-O-Meter

War-O-Meter monitors dramatic probability swings on Polymarket's "Will the US attack Iran?" market and sends real-time alerts to Telegram.

## Features

- Monitors Polymarket event odds in real-time
- Detects significant price movements (configurable threshold)
- Sends instant Telegram alerts when irregularities are detected
- Configurable polling interval and alert cooldown
- Tracks multiple markets within an event

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Requires Python 3.12+

### 2. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the prompts
3. Copy the bot token provided

### 3. Get Your Chat ID

1. Search for `@userinfobot` on Telegram
2. Send `/start` to get your user ID
3. Use this ID as your `TELEGRAM_CHAT_ID`

Alternatively, for a channel:
1. Add your bot to the channel as an admin
2. Use the channel's username (e.g., `@mychannel`) or numeric ID

### 4. Configure Environment

Edit `.env` with your configuration:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
EVENT_SLUG=us-strikes-iran-by
POLL_INTERVAL_SECONDS=60
PRICE_CHANGE_THRESHOLD=0.05
ALERT_COOLDOWN_SECONDS=300
```

## Usage

Run the monitor:

```bash
python monitor.py
```

The monitor will:
1. Send a startup notification to Telegram
2. Fetch current market odds from Polymarket
3. Check for price changes every 60 seconds (configurable)
4. Send an alert when any market's YES price changes by more than 5% (configurable)

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | - | Your Telegram bot token from BotFather |
| `TELEGRAM_CHAT_ID` | - | Telegram chat/user/channel ID for alerts |
| `EVENT_SLUG` | `us-strikes-iran-by` | Polymarket event URL slug |
| `POLL_INTERVAL_SECONDS` | `60` | How often to check prices (seconds) |
| `PRICE_CHANGE_THRESHOLD` | `0.05` | Price change threshold (0.05 = 5%) |
| `ALERT_COOLDOWN_SECONDS` | `300` | Minimum time between alerts for same market |

## Alert Format

When a price irregularity is detected, you'll receive an alert like:

```
🚨 ALERT: Price UP

Market: Will the US strike Iran by March 2025?
Old: 15.0% -> New: 22.0%
Change: +7.0%
Time: 2025-01-31 12:30:45 UTC
```

## Monitoring Other Events

To monitor a different Polymarket event:

1. Go to the event page on Polymarket
2. Copy the slug from the URL (e.g., `https://polymarket.com/event/your-event-slug`)
3. Set `EVENT_SLUG=your-event-slug` in your `.env` file

## License

MIT
