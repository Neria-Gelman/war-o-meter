import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Telegram settings
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # Polymarket settings
    GAMMA_API_URL: str = "https://gamma-api.polymarket.com"
    EVENT_SLUG: str = os.getenv("EVENT_SLUG", "us-strikes-iran-by")

    # Monitoring settings
    POLL_INTERVAL_SECONDS: int = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    PRICE_CHANGE_THRESHOLD: float = float(os.getenv("PRICE_CHANGE_THRESHOLD", "0.05"))  # 5% change
    ALERT_COOLDOWN_SECONDS: int = int(os.getenv("ALERT_COOLDOWN_SECONDS", "300"))  # 5 minutes
