from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
import os
import signal
import socket

# Server configuration
HOST = '::'
PORT = 4000

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    # Add basic response caching
    protocol_version = 'HTTP/1.1'
    def end_headers(self):
        self.send_header('Cache-Control', 'max-age=60')  # Cache for 60 seconds
        super().end_headers()

class IPv6Server(HTTPServer):
    address_family = socket.AF_INET6

httpd = None

def signal_handler(sig, frame):
    print('\nShutting down the server...')
    if httpd:
        httpd.shutdown()
        httpd.server_close()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

try:
    if not (os.path.exists('cert.pem') and os.path.exists('key.pem')):
        print("Error: Certificate files not found.")
        exit(1)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')

    httpd = IPv6Server((HOST, PORT, 0, 0), CustomHTTPRequestHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Server running on https://[::]{PORT}")
    print("Press Ctrl+C to shut down")
    httpd.serve_forever()

except Exception as e:
    print(f"Error: {e}")
