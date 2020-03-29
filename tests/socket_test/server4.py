import socket
from multiprocessing import Process
from threading import Thread

class work(Thread):
    def __init__(self, sock):
        super().__init__()
        self.sock = sock

    def run(self):
        data = self.sock.recv(100).decode()
        self.sock.send(data.encode())
        self.sock.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 12360))
server.listen(20)
while True:
    client, addr = server.accept()
    work(client).start()