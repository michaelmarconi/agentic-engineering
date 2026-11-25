"""Prints the time taken to attach a 10,000,000-byte file."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.attachments import attach

data = b"x" * 10_000_000
start = time.perf_counter()
attach({"number": 17}, data)
print(f"{time.perf_counter() - start:.3f} seconds")
