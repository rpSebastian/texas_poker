import time
import socket
import multiprocessing


class main(multiprocessing.Process):
    def __init__(self, i):
        super().__init__()
        self.i = i

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 8123))

        client.send('xxx' + str(self.i)).encode())
        data = client.recv(100).decode()


a = time.time()
processes = []
for i in range(2):
    p = main(i)
    p.start()
    processes.append(p)
for p in processes:
    p.join()

print(time.time() - a)
