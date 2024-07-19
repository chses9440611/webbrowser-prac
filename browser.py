import socket
import ssl
class URL:
    def __init__(self, url):
        # http://example.org/hello
        self.scheme, url = url.split("://", 1)
        assert self.scheme in  ["http", "https"]

        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
        if "/" not in url:
            url += "/"
        # example.com / hello
        self.host, url = url.split("/", 1)
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        self.path = "/" + url

    def connect(self):
        self.s = socket.socket(
                family = socket.AF_INET,
                type = socket.SOCK_STREAM,
                proto = socket.IPPROTO_TCP,
                )
        self.s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            self.s = ctx.wrap_socket(self.s, server_hostname = self.host)



    def send_request(self):
        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n"
        self.s.send(request.encode("utf-8"))

    def get_response_body(self):
        response  = self.s.makefile("r", encoding="utf8", newline="\r\n")
        # HTTP/1.x 200 OK
        statusline = response.readline()
        version, status, explain = statusline.split(" ", 2)
        if int(status) != 200:
            print(statusline)
        self.response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value =  line.split(":", 1)
            self.response_headers[header] = value.strip()

        assert "transfer-encoding" not in self.response_headers
        assert "content-encoding" not in self.response_headers
        content = response.read()
        return content

    def disconnect(self):
        self.s.close()

def show(body):
    in_flag = False
    for c in body:
        if c == "<":
            in_flag = True
        elif c == ">":
            in_flag = False
        elif not in_flag:
            print(c, end = "")

def load(url):
    url.connect()
    body = url.send_request()
    body= url.get_response_body()
    url.disconnect()
    return body

    


if __name__ == "__main__":
    import sys
    content = load(URL(sys.argv[1]))
    show(content)


        
