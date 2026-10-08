import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))


def create_server():
    return HTTPServer((HOST, PORT), SimpleHTTPRequestHandler)


if __name__ == "__main__":
    server = create_server()
    print(f"Server running on port {PORT}")
    server.serve_forever()