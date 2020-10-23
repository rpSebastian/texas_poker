import sys
import json
import struct
import socket

server_ip = "holdem.ia.ac.cn"
server_port = 18888
room_id = 888891
room_number = 2
# bots = ["LooseAggressive","TightPassive"]
bots = ["RandomGambler","CandidStatistician"]
game_number = 2
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
    print(server_ip, server_port)
    client.connect((server_ip, server_port))
    print("connect")
    message = dict(info='ai_vs_ai', room_id=room_id, room_number=room_number, bots=bots, game_number=game_number)
    sendJson(client, message)
    print("send")
    num = 0
    while True:
        # print("recving")
        data = recvJson(client)
        print(data)
        if data['info'] == 'result':
            num += 1
            print(num)
        if data['info'] == 'error' or data['info'] == 'success':
            print(data)
            break
    client.close()
