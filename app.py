import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))


class HealthCheckHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"healthy")
            return

        super().do_GET()


def create_server():
    return HTTPServer((HOST, PORT), HealthCheckHandler)


if __name__ == "__main__":
    server = create_server()
    print(f"Server running on port {PORT}")
    server.serve_forever()