"""Handle update messages from the customs broker."""
from datetime import datetime

from shipments import record_status


def handle(message: dict) -> None:
    at = datetime.fromisoformat(message["time"])
    if message["type"] == "hold":
        record_status(message["container"], "held", at)
    # Other message types, such as "released", are ignored for now.
