from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict

from src.config import Config
from src.polymarket_client import Market


@dataclass
class PriceSnapshot:
    market_id: str
    question: str
    yes_price: float
    no_price: float
    timestamp: datetime


@dataclass
class Alert:
    market_id: str
    question: str
    alert_type: str  # "spike" or "drop"
    old_price: float
    new_price: float
    change_percent: float
    timestamp: datetime

    def format_message(self) -> str:
        """Format the alert as a human-readable message."""
        direction = "UP" if self.alert_type == "spike" else "DOWN"
        emoji = "🚨" if abs(self.change_percent) > 0.10 else "⚠️"

        return (
            f"{emoji} ALERT: Price {direction}\n\n"
            f"Market: {self.question}\n"
            f"Old: {self.old_price:.1%} -> New: {self.new_price:.1%}\n"
            f"Change: {self.change_percent:+.1%}\n"
            f"Time: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )


class IrregularityDetector:
    def __init__(self, threshold: float | None = None, cooldown_seconds: int | None = None):
        self.threshold = threshold or Config.PRICE_CHANGE_THRESHOLD
        self.cooldown = timedelta(seconds=cooldown_seconds or Config.ALERT_COOLDOWN_SECONDS)
        self.price_history: Dict[str, PriceSnapshot] = {}
        self.last_alert_time: Dict[str, datetime] = {}

    def check_market(self, market: Market) -> Alert | None:
        """Check a market for price irregularities. Returns an Alert if detected."""
        now = datetime.utcnow()
        market_id = market.id

        # Get previous snapshot
        previous = self.price_history.get(market_id)

        # Create current snapshot
        current = PriceSnapshot(
            market_id=market_id,
            question=market.question,
            yes_price=market.outcome_yes_price,
            no_price=market.outcome_no_price,
            timestamp=now,
        )

        # Store current snapshot for next comparison
        self.price_history[market_id] = current

        # If no previous data, nothing to compare
        if previous is None:
            return None

        # Check cooldown
        last_alert = self.last_alert_time.get(market_id)
        if last_alert and (now - last_alert) < self.cooldown:
            return None

        # Calculate price change (using YES price as primary indicator)
        price_change = current.yes_price - previous.yes_price

        # Check if change exceeds threshold
        if abs(price_change) >= self.threshold:
            alert_type = "spike" if price_change > 0 else "drop"
            alert = Alert(
                market_id=market_id,
                question=market.question,
                alert_type=alert_type,
                old_price=previous.yes_price,
                new_price=current.yes_price,
                change_percent=price_change,
                timestamp=now,
            )
            self.last_alert_time[market_id] = now
            return alert

        return None

    def check_markets(self, markets: list[Market]) -> list[Alert]:
        """Check multiple markets and return all alerts."""
        alerts = []
        for market in markets:
            alert = self.check_market(market)
            if alert:
                alerts.append(alert)
        return alerts

    def get_status(self) -> dict:
        """Get current monitoring status."""
        return {
            "tracked_markets": len(self.price_history),
            "threshold": self.threshold,
            "cooldown_seconds": self.cooldown.total_seconds(),
            "markets": {
                mid: {
                    "question": snap.question,
                    "yes_price": f"{snap.yes_price:.1%}",
                    "last_update": snap.timestamp.isoformat(),
                }
                for mid, snap in self.price_history.items()
            },
        }
