from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer, HTTPServer
import socket


def _get_ip():
    ips = socket.getaddrinfo(socket.gethostname(), 80)
    for ip in ips:
        if ip[4][0].startswith('24'):
            return ip[4][0]


class _Request(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            self.send_response(200)
            self.end_headers()
            self.get(self.path)
        except Exception as e:
            self.get_error(e)

    def do_POST(self):
        try:
            self.send_response(200)
            self.end_headers()
            self.post(self.path, self.read())
        except Exception as e:
            self.post_error(e)

    def get(self, path):
        pass

    def post(self, path, data):
        pass

    def get_error(self, error):
        pass

    def post_error(self, error):
        pass

    def read(self):
        remainbytes = int(self.headers['content-length'])
        return self.rfile.read(remainbytes)

    def write(self, content):
        self.wfile.write(content)


class Request(_Request):

    def get(self, path):
        pass

    def post(self, path, data):
        pass

    def get_error(self, error):
        pass

    def post_error(self, error):
        pass


def run(ip=None, port=8000, processor=Request):
    ip = ip or _get_ip()
    host = (ip, port)
    family = socket.getaddrinfo(*host)[0][0]
    HTTPServer.address_family = family
    server = ThreadingHTTPServer(host, processor)
    print("Starting server, listen at: [{}]:{}".format(*host))
    server.serve_forever()
