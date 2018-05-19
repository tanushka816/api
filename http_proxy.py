import socket
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn, TCPServer
import select
from threading import Thread

ADS = ['doubleclick.net', 'reklama.e1.ru', 'reklama.ngs.ru', 'mc.yandex.ru', 'rs.mail.ru',
       'r.mradx.net', 'goto.msk.ru',  "market.yandex.ru", "connect.ok.ru", "an.yandex.ru",
       "aflt.market.yandex.ru", "pagead2.googlesyndication.com", "securepubads.g.doubleclick.net"]


class MyThreadingTCPServer(ThreadingMixIn, TCPServer):
    """To create a separate process or thread to handle each request
ThreadingMixIn mix-in classes can be used to support asynchronous behaviour
 the default flag is False
 meaning that Python will not exit
 until all threads created by ThreadingMixIn have exited
 The mix-in class overrides a method defined in TCPServer. """
    pass


class MyADBlocker(SimpleHTTPRequestHandler):

    def do_CONNECT(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host, port = self.path.split(":")

        for ads_host in ADS:
            if host in ads_host:
                self.send_error(423, f"ADS blocked from host: {host}")
                return
        sock.connect((host, int(port)))
        self.send_response(200)
        self.send_header("proxy ads blocker", '')
        self.end_headers()

        cur_connections = [self.connection, sock]
        while True:
            inputready, outputready, exceptready = select.select(cur_connections, [], cur_connections, 0.1)
            if exceptready:
                break
            for connect in inputready:
                data = connect.recv(8192)
                if data:
                    if connect is cur_connections[0]:
                        cur_connections[1].sendall(data)
                    else:
                        cur_connections[0].sendall(data)
        sock.close()

    def do_GET(self):
        self.copyfile(f, self.wfile)


if __name__ == "__main__":
    server = MyThreadingTCPServer(('127.0.0.1', 8080), MyADBlocker)
    thread = Thread(target=server.serve_forever)
    thread.start()
