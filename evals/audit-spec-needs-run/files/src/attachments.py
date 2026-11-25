"""Attach files to invoices."""

LIMIT = 10_000_000


class TooLarge(Exception):
    pass


def attach(invoice, data):
    if len(data) > LIMIT:
        raise TooLarge(f"{len(data)} bytes is over the {LIMIT}-byte limit")
    invoice.setdefault("attachments", []).append(bytes(data))
