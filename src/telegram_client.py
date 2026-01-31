import asyncio
import logging

from telegram import Bot
from telegram.constants import ParseMode

from src.config import Config

logger = logging.getLogger(__name__)


class TelegramAlertClient:
    def __init__(self, token: str | None = None, chat_id: str | None = None):
        self.token = token or Config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or Config.TELEGRAM_CHAT_ID
        self._bot: Bot | None = None

    @property
    def bot(self) -> Bot:
        if self._bot is None:
            if not self.token:
                raise ValueError("TELEGRAM_BOT_TOKEN is not configured")
            self._bot = Bot(token=self.token)
        return self._bot

    async def send_alert(self, message: str) -> bool:
        """Send an alert message to the configured Telegram chat."""
        if not self.chat_id:
            logger.error("TELEGRAM_CHAT_ID is not configured")
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            logger.info(f"Alert sent to chat {self.chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False

    async def send_plain_alert(self, message: str) -> bool:
        """Send a plain text alert without markdown parsing."""
        if not self.chat_id:
            logger.error("TELEGRAM_CHAT_ID is not configured")
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
            )
            logger.info(f"Alert sent to chat {self.chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False


def send_alert_sync(message: str) -> bool:
    """Synchronous wrapper for sending alerts."""
    client = TelegramAlertClient()
    return asyncio.run(client.send_plain_alert(message))


def escape_markdown_v2(text: str) -> str:
    """Escape special characters for MarkdownV2."""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text
