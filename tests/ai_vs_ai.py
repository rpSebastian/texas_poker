import sys
import json
import struct
import socket

server_ip = "127.0.0.1"
server_port = 18888
room_id = int(sys.argv[1]) if len(sys.argv) > 0 else 100
room_number = 2
bots = ["CallAgent", "CallAgent"]
game_number = 100

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
    message = dict(info='ai_vs_ai', room_id=room_id, room_number=2, bots=bots, game_number=game_number)
    sendJson(client, message)
    num = 0
    while True:
        data = recvJson(client)
        print(data['info'])
        if data['info'] == 'result':
            num += 1
            print(num)
    client.close()
