"""Bookings."""

SLOTS = {}


def book(slot, customer):
    SLOTS[slot] = customer
    return True
