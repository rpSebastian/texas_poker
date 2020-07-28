import sys
import json
import struct
import socket

server_ip = "172.18.40.65"
server_port = 18888
room_id = int(sys.argv[1])
room_number = 2
bots = ["RandomAgent", "CallAgent"]
game_number = 10
# mode = "duplicate"

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
    message = dict(info='ai_vs_ai', room_id=room_id, room_number=room_number, bots=bots, game_number=game_number, deposit=True)
    sendJson(client, message)
    num = 0
    while True:
        data = recvJson(client)
        if data['info'] == 'result':
            num += 1
            print(num)
        if data['info'] == 'error' or data['info'] == 'success':
            print(data)
            break
    client.close()
