#!/usr/local/bin/python3

# params
local_port = 8080
dest_host = "localhost"
dest_port = 8000

try:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except:
    from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

# listen on port 8000 of the localhost
addy = ('',local_port)

# define the http handler
class httpd_handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = "http://%s:%s%s"%(dest_host, dest_port, self.path)
        print ("Fetching %s"%url)

        r = requests.get(url)

        self.send_response(r.status_code)
        for k in r.headers:
            self.send_header(k, r.headers[k])
        self.end_headers()
        self.wfile.write(r.content)

    def do_POST(self):
        return do_GET(self)

# create http daemon
print("Starting HTTP Proxy -> redirecting port %s to %s:%s"%(local_port, dest_host, dest_port))
httpd = HTTPServer(addy,httpd_handler)
try:
    import ssl
    httpd.socket = ssl.wrap_socket (httpd.socket, 
            keyfile="key.pem", 
            certfile='cert.pem', server_side=True)
except:
    print("Error attempting SSL, no HTTPS")
httpd.serve_forever()
