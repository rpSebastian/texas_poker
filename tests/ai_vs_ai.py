import sys
import json
import struct
import socket

server_ip = "bb.xuhang.ink"
server_port = 12345
room_id = 100
room_number = 2
bots = ["CallAgent", "CallAgent"]
game_number = 1


def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data)))
    request.sendall(data)


def recvJson(request):
    length = struct.unpack('i', request.recv(4))[0]
    data = request.recv(length).decode()
    while len(data) != length:
        data = data + request.recv(length - len(data)).decode()
    data = json.loads(data)
    return data


if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    message = dict(info='ai_vs_ai', room_id=room_id, room_number=2, bots=bots, game_number=game_number)
    sendJson(client, message)
    num = 0
    while True:
        data = recvJson(client)
        print(data)
        if data['info'] == 'result':
            num += 1
            print(num)
    client.close()
