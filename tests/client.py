import json
import struct
import socket

server_ip = "127.0.0.1"
server_port = 18888
room_id = 1000
room_number = 2
bots = ["RandomAgent"]
game_number = 2

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
    message = dict(info='connect', room_id=room_id, name='xxx', room_number=room_number, bots=bots, game_number=game_number)
    sendJson(client, message)
    while True:
        data = recvJson(client)
        print(data)
        if data['info'] == 'state' and data['position'] == data['action_position']:
            position = data['position']
            if 'call' in data['legal_actions']:
                action = 'call'
            else:
                action = 'check'
            sendJson(client, {'action': 'fold', 'info': 'action'})
        if data['info'] == 'result':
            print('win money: {},\tyour card: {},\topp card: {},\t\tpublic card: {}'.format(data['players'][position]['win_money'], data['player_card'][position],  data['player_card'][1-position], data['public_card']))
            sendJson(client, {'info': 'ready', 'status': 'start'})
            break
    client.close()
