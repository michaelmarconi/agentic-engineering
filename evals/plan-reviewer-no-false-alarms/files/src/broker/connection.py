"""The connection to the customs broker, which sends hold and release messages."""
import socket

BROKER = ("broker.example", 7000)


def connect(timeout: float = 10) -> socket.socket:
    return socket.create_connection(BROKER, timeout=timeout)
