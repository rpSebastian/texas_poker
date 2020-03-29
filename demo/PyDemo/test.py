import json
import struct
import socket

server_ip = "poker.xuhang.ink"
server_port = 18888
room_id = 121
room_number = 2
bots = ["CallAgent", "CallAgent"]


def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data)))
    request.sendall(data)


def recvJson(request):
    length = struct.unpack('i', request.recv(4))[0]
    data = json.loads(request.recv(length).decode())
    return data


if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    message = dict(info='ai_vs_ai', room_id=room_id, room_number=2, bots=bots)
    sendJson(client, message)
    while True:
        data = recvJson(client)
        print(data)
    client.close()
