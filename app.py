from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 8000))

server = HTTPServer((HOST, PORT), SimpleHTTPRequestHandler)

print(f"Server running on port {PORT}")

server.serve_forever()