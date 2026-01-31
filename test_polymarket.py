#!/usr/bin/env python3
"""Simple test to verify Polymarket API works - no external dependencies needed."""

import json
import urllib.request
import urllib.error

EVENT_SLUG = "us-strikes-iran-by"
GAMMA_API_URL = "https://gamma-api.polymarket.com"


def test_polymarket():
    """Test fetching data from Polymarket."""
    print("=" * 50)
    print("Testing Polymarket API...")
    print(f"Event slug: {EVENT_SLUG}")
    print("-" * 50)

    url = f"{GAMMA_API_URL}/events?slug={EVENT_SLUG}"
    print(f"URL: {url}\n")

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "war-o-meter/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        if not data:
            print("WARNING: No events found for this slug")
            return False

        event = data[0]
        print(f"Event: {event.get('title', 'N/A')}")
        print(f"Volume: ${float(event.get('volume', 0)):,.0f}")
        print(f"Liquidity: ${float(event.get('liquidity', 0)):,.0f}")
        print()

        markets = event.get("markets", [])
        if not markets:
            print("WARNING: No markets in this event")
            return False

        print(f"Found {len(markets)} market(s):\n")
        for market in markets:
            question = market.get("question", "N/A")
            outcome_prices = market.get("outcomePrices", "[]")

            if isinstance(outcome_prices, str):
                outcome_prices = json.loads(outcome_prices)

            yes_price = float(outcome_prices[0]) if outcome_prices else 0
            no_price = float(outcome_prices[1]) if len(outcome_prices) > 1 else 0

            print(f"  Question: {question}")
            print(f"  YES: {yes_price * 100:.1f}%")
            print(f"  NO:  {no_price * 100:.1f}%")
            print(f"  Volume: ${float(market.get('volume', 0)):,.0f}")
            print()

        print("-" * 50)
        print("Polymarket API: OK")
        return True

    except urllib.error.URLError as e:
        print(f"ERROR: Network error - {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse response - {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    print("\nWar-O-Meter - Polymarket Connection Test")
    success = test_polymarket()
    print()

    if success:
        print("Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your Telegram bot token and chat ID")
        print("3. Run: python monitor.py")
    else:
        print("Fix the errors above before running the monitor.")
