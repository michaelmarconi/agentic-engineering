"""A tiny notes service. GET /health answers ok."""
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"ok" if self.path == "/health" else b"notes"
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    HTTPServer(("localhost", 8000), Handler).serve_forever()
