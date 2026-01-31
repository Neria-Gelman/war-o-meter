import json
from dataclasses import dataclass
from datetime import datetime

import httpx

from src.config import Config


@dataclass
class Market:
    id: str
    question: str
    outcome_yes_price: float
    outcome_no_price: float
    volume: float
    liquidity: float
    end_date: str | None
    active: bool
    closed: bool

    @property
    def yes_percent(self) -> float:
        return self.outcome_yes_price * 100

    @property
    def no_percent(self) -> float:
        return self.outcome_no_price * 100


@dataclass
class Event:
    id: str
    title: str
    slug: str
    description: str
    markets: list[Market]
    volume: float
    liquidity: float
    start_date: str | None
    end_date: str | None


class PolymarketClient:
    def __init__(self):
        self.base_url = Config.GAMMA_API_URL
        self.client = httpx.Client(timeout=30.0)

    def get_event_by_slug(self, slug: str) -> Event | None:
        """Fetch an event by its URL slug."""
        url = f"{self.base_url}/events"
        params = {"slug": slug}

        response = self.client.get(url, params=params)
        response.raise_for_status()

        events = response.json()
        if not events:
            return None

        event_data = events[0]
        return self._parse_event(event_data)

    def get_markets_for_event(self, event_slug: str) -> list[Market]:
        """Get all markets associated with an event slug."""
        event = self.get_event_by_slug(event_slug)
        if not event:
            return []
        return event.markets

    def _parse_event(self, data: dict) -> Event:
        """Parse event data from API response."""
        markets = []
        if "markets" in data:
            for market_data in data["markets"]:
                market = self._parse_market(market_data)
                if market:
                    markets.append(market)

        return Event(
            id=str(data.get("id", "")),
            title=data.get("title", ""),
            slug=data.get("slug", ""),
            description=data.get("description", ""),
            markets=markets,
            volume=float(data.get("volume", 0) or 0),
            liquidity=float(data.get("liquidity", 0) or 0),
            start_date=data.get("startDate"),
            end_date=data.get("endDate"),
        )

    def _parse_market(self, data: dict) -> Market | None:
        """Parse market data from API response."""
        outcome_prices = data.get("outcomePrices")
        if isinstance(outcome_prices, str):
            try:
                outcome_prices = json.loads(outcome_prices)
            except json.JSONDecodeError:
                outcome_prices = [0, 0]

        if not outcome_prices or len(outcome_prices) < 2:
            outcome_prices = [0, 0]

        yes_price = float(outcome_prices[0]) if outcome_prices[0] else 0
        no_price = float(outcome_prices[1]) if outcome_prices[1] else 0

        return Market(
            id=str(data.get("id", "")),
            question=data.get("question", ""),
            outcome_yes_price=yes_price,
            outcome_no_price=no_price,
            volume=float(data.get("volume", 0) or 0),
            liquidity=float(data.get("liquidity", 0) or 0),
            end_date=data.get("endDate"),
            active=data.get("active", False),
            closed=data.get("closed", False),
        )

    def close(self):
        """Close the HTTP client."""
        self.client.close()


def get_current_odds(event_slug: str | None = None) -> list[Market]:
    """Convenience function to fetch current odds for the configured event."""
    slug = event_slug or Config.EVENT_SLUG
    client = PolymarketClient()
    try:
        return client.get_markets_for_event(slug)
    finally:
        client.close()
