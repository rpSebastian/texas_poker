import socket
import json
import time
import struct
import multiprocessing

myip = "127.0.0.1"
myport = 18888
room_id = 1000

def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data)))
    request.sendall(data)


def recvJson(request):
    length = struct.unpack('i', request.recv(4))[0]
    data = json.loads(request.recv(length).decode())
    return data


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((myip, myport))
sendJson(client, {'info': 'observer', 'room_id': room_id})
while True:
    data = recvJson(client)
    print(data)
