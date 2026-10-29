"""Shipment status events (ADR 0003)."""
from datetime import datetime

EVENTS = []


def record_status(container: str, status: str, at: datetime) -> None:
    """Record a status change as an event; the only way a status changes."""
    EVENTS.append({"container": container, "status": status, "at": at})


def latest(container: str):
    found = [e for e in EVENTS if e["container"] == container]
    return found[-1] if found else None
