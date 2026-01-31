#!/usr/bin/env python3
"""
War-O-Meter: Monitor Polymarket odds for dramatic probability swings
and send alerts to Telegram.
"""

import asyncio
import logging
import signal
import sys
import time
from datetime import datetime

from src.config import Config
from src.detector import IrregularityDetector
from src.polymarket_client import PolymarketClient
from src.telegram_client import TelegramAlertClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("war-o-meter")


class Monitor:
    def __init__(self):
        self.polymarket = PolymarketClient()
        self.telegram = TelegramAlertClient()
        self.detector = IrregularityDetector()
        self.running = False

    async def send_startup_message(self):
        """Send a startup notification."""
        message = (
            f"🔔 War-O-Meter Started\n\n"
            f"Monitoring: {Config.EVENT_SLUG}\n"
            f"Threshold: {Config.PRICE_CHANGE_THRESHOLD:.0%}\n"
            f"Poll interval: {Config.POLL_INTERVAL_SECONDS}s"
        )
        await self.telegram.send_plain_alert(message)

    async def check_and_alert(self):
        """Fetch current odds and send alerts for any irregularities."""
        try:
            markets = self.polymarket.get_markets_for_event(Config.EVENT_SLUG)

            if not markets:
                logger.warning(f"No markets found for event: {Config.EVENT_SLUG}")
                return

            logger.info(f"Fetched {len(markets)} markets")
            for market in markets:
                logger.debug(
                    f"  - {market.question}: YES={market.yes_percent:.1f}%"
                )

            # Check for irregularities
            alerts = self.detector.check_markets(markets)

            # Send alerts
            for alert in alerts:
                message = alert.format_message()
                logger.warning(f"Alert triggered: {message}")
                await self.telegram.send_plain_alert(message)

        except Exception as e:
            logger.error(f"Error during check: {e}")

    async def run(self):
        """Main monitoring loop."""
        self.running = True
        logger.info("Starting War-O-Meter monitor...")
        logger.info(f"Event slug: {Config.EVENT_SLUG}")
        logger.info(f"Poll interval: {Config.POLL_INTERVAL_SECONDS}s")
        logger.info(f"Price change threshold: {Config.PRICE_CHANGE_THRESHOLD:.0%}")

        # Send startup message
        if Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_CHAT_ID:
            await self.send_startup_message()
        else:
            logger.warning(
                "Telegram not configured - alerts will only be logged"
            )

        # Initial check
        await self.check_and_alert()

        # Main loop
        while self.running:
            await asyncio.sleep(Config.POLL_INTERVAL_SECONDS)
            await self.check_and_alert()

    def stop(self):
        """Stop the monitor."""
        logger.info("Stopping monitor...")
        self.running = False
        self.polymarket.close()


async def main():
    monitor = Monitor()

    # Handle shutdown signals
    def signal_handler(signum, frame):
        monitor.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())
