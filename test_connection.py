#!/usr/bin/env python3
"""Test script to verify War-O-Meter components work correctly."""

import asyncio
import sys

from src.config import Config
from src.polymarket_client import PolymarketClient
from src.telegram_client import TelegramAlertClient


def test_polymarket():
    """Test fetching data from Polymarket."""
    print("=" * 50)
    print("Testing Polymarket API...")
    print(f"Event slug: {Config.EVENT_SLUG}")
    print("-" * 50)

    client = PolymarketClient()
    try:
        markets = client.get_markets_for_event(Config.EVENT_SLUG)

        if not markets:
            print("WARNING: No markets found for this event")
            return False

        print(f"Found {len(markets)} market(s):\n")
        for market in markets:
            print(f"  Market: {market.question}")
            print(f"  YES: {market.yes_percent:.1f}%")
            print(f"  NO:  {market.no_percent:.1f}%")
            print(f"  Volume: ${market.volume:,.0f}")
            print(f"  Active: {market.active}")
            print()

        print("Polymarket API: OK")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        client.close()


async def test_telegram():
    """Test sending a message via Telegram."""
    print("=" * 50)
    print("Testing Telegram Bot...")
    print("-" * 50)

    if not Config.TELEGRAM_BOT_TOKEN:
        print("SKIP: TELEGRAM_BOT_TOKEN not configured")
        return None

    if not Config.TELEGRAM_CHAT_ID:
        print("SKIP: TELEGRAM_CHAT_ID not configured")
        return None

    print(f"Chat ID: {Config.TELEGRAM_CHAT_ID}")

    client = TelegramAlertClient()
    try:
        success = await client.send_plain_alert(
            "Test message from War-O-Meter\n\nIf you see this, Telegram alerts are working!"
        )

        if success:
            print("Telegram Bot: OK - Check your Telegram!")
            return True
        else:
            print("Telegram Bot: FAILED")
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    print("\nWar-O-Meter Component Test")
    print("=" * 50)
    print()

    # Test Polymarket
    polymarket_ok = test_polymarket()
    print()

    # Test Telegram
    telegram_result = asyncio.run(test_telegram())
    print()

    # Summary
    print("=" * 50)
    print("Summary:")
    print(f"  Polymarket API: {'OK' if polymarket_ok else 'FAILED'}")
    if telegram_result is None:
        print("  Telegram Bot:   SKIPPED (not configured)")
    else:
        print(f"  Telegram Bot:   {'OK' if telegram_result else 'FAILED'}")
    print("=" * 50)

    if polymarket_ok and telegram_result is not False:
        print("\nReady to run: python monitor.py")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
