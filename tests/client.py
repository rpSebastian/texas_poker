import json
import struct
import socket
import time
server_ip = "holdem.ia.ac.cn"
server_port = 18888
room_id = 1000006
room_number = 2
game_number = 3
bots = []


def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data))+data)


def recvJson(request):
    length = struct.unpack('i', request.recv(4))[0]
    data = json.loads(request.recv(length).decode())
    return data


if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    message = dict(info='connect', room_id=room_id, name='test', room_number=room_number, bots=bots, game_number=game_number)
    sendJson(client, message)
    num = 0
    start = time.time()
    while True:
        data = recvJson(client)
        print(data)
        if 'position' in data:
            position = data['position']
        if data['info'] == 'state':
            # print(data["private_card"])
            if data['position'] == data['action_position']:
                if 'call' in data['legal_actions']:
                    action = 'call'
                else:
                    action = 'check'
                action = input()
                sendJson(client, {'action': action, 'info': 'action'})
                # start = time.time()
        elif data['info'] == 'result':
            # print(data['player_card'])
            print('win money: {},\tyour card: {},\topp card: {},\t\tpublic card: {}'.format(data['players'][position]['win_money'], data['player_card'][position],  data['player_card'][1-position], data['public_card']))
            num += 1
            sendJson(client, {'info': 'ready', 'status': 'start'})
        else:
            print(data)
            break
    client.close()
    print(game_number, time.time() - start)

