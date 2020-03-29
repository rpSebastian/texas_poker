import time
import socket
import multiprocessing


class main(multiprocessing.Process):
    def __init__(self):
        super().__init__()

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 12357))
        client.send('call'.encode())
        data = client.recv(100).decode()

for i in range(10000):
    main().start()