"""Serve the frontend and proxy /tasks to the FastAPI app on port 8000."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
import urllib.error
import urllib.request

API = "http://127.0.0.1:8000"
ROOT = os.path.dirname(os.path.abspath(__file__))
HOST = "127.0.0.1"
PORT = 5500


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        if self.path.startswith("/tasks"):
            self._proxy()
        else:
            super().do_GET()

    def do_POST(self):
        self._proxy_or_reject()

    def do_PATCH(self):
        self._proxy_or_reject()

    def do_DELETE(self):
        self._proxy_or_reject()

    def _proxy_or_reject(self):
        if self.path.startswith("/tasks"):
            self._proxy()
        else:
            self.send_error(405, "Method not allowed")

    def _proxy(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        headers = {}
        content_type = self.headers.get("Content-Type")
        if content_type:
            headers["Content-Type"] = content_type
        elif body:
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            API + self.path,
            data=body,
            method=self.command,
            headers=headers,
        )

        try:
            with urllib.request.urlopen(request) as response:
                self._write_proxied(response.status, response.headers, response.read())
        except urllib.error.HTTPError as error:
            self._write_proxied(error.code, error.headers, error.read())
        except urllib.error.URLError:
            payload = b'{"error":"API is not reachable. Start uvicorn on port 8000."}'
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    def _write_proxied(self, status, headers, data):
        self.send_response(status)
        content_type = headers.get("Content-Type", "application/json")
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Frontend: http://{HOST}:{PORT}", flush=True)
    print(f"Proxying /tasks -> {API}", flush=True)
    httpd.serve_forever()
