import gevent 
import gevent.monkey
gevent.monkey.patch_all()

import socket
import json
import struct
import time

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

def client(i):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 10000))
    s.send("hello".encode())
    data = s.recv(1024).decode()
    # print(data)
    

start = time.time()
tasks = []
for i in range(1):
    tasks.append(gevent.spawn(client, i))
    # tasks.append(gevent.spawn(client, i))
gevent.joinall(tasks)
end = time.time() - start
print(end)