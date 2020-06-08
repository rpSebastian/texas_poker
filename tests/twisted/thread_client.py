import time
import socket
import multiprocessing

import json
import struct


def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data)))
    request.sendall(data)


def recvJson(request):
    data = request.recv(4)
    length = struct.unpack('i', data)[0]
    data = request.recv(length).decode()
    while len(data) != length:
        data = data + request.recv(length - len(data)).decode()
    data = json.loads(data)
    return data
   

class main(multiprocessing.Process):
    def __init__(self, i):
        super().__init__()
        self.i = i

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 1234))
        for i in range(10):
            import time
            time.sleep(1)
            sendJson(client, ['Hello'])
            data = recvJson(client)
            print(data)


a = time.time()
processes = []
for i in range(1):
    p = main(i)
    p.start()
    processes.append(p)
for p in processes:
    p.join()
print(time.time() - a)
