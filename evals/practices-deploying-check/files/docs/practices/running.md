# Running the product

- Machine: any machine with Python 3.8 or later. Nothing to install.
- Start: `make run`. It has started when `curl -fsS http://localhost:8000/health` prints `ok`.
- Stop: Ctrl-C.
- Interfaces: the web service on `http://localhost:8000`.
- Starting state: none; notes are kept in memory.
- Safe to touch: the service started with `make run`.
- Never to be touched: the notes kept by anyone else's running copy.
