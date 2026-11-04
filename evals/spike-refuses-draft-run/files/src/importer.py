"""Reads the bank's statement file into ledger rows."""

import csv


def read_statement(path):
    """Return the statement's transactions as lists of [date, payee, amount], header left out."""
    with open(path, newline="", encoding="utf-8") as f:
        return [row for row in csv.reader(f, delimiter=";")][1:]
