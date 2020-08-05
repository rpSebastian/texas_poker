import gevent
import gevent.monkey
gevent.monkey.patch_all()

import json
import struct
import socket
import time
import multiprocessing

server_ip = "127.0.0.1"
server_port = 60010
room_id = 1000000
room_number = 2
bots = []
game_number = 20
game = 10

def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data))+data)


def recvJson(request):
    length = struct.unpack('i', request.recv(4))[0]
    data = json.loads(request.recv(length).decode())
    return data

def func(room_id, number):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    message = dict(info='connect', room_id=room_id, name='xxx', room_number=room_number, bots=bots, game_number=game_number)
    sendJson(client, message)

    while True:
        data = recvJson(client)
        if 'position' in data:
            position = data['position']
        if data['info'] == 'state':
            if data['position'] == data['action_position']:
                if 'call' in data['legal_actions']:
                    action = 'call'
                else:
                    action = 'check'
                sendJson(client, {'action': action, 'info': 'action'})
        elif data['info'] == 'result': 
            # print('win money: {},\tyour card: {},\topp card: {},\t\tpublic card: {}'.format(data['players'][position]['win_money'], data['player_card'][position],  data['player_card'][1-position], data['public_card']))
            sendJson(client, {'info': 'ready', 'status': 'start'})
        else:
            # print(data)
            break
    client.close()

def task(num, game_count):
    tasks = []
    for room_id in range(game_count):
        tasks.append(gevent.spawn(func, game_count * num + room_id, 1))
        tasks.append(gevent.spawn(func, game_count * num + room_id, 2))
    gevent.joinall(tasks)

if __name__ == "__main__":
    tasks = []
    start = time.time()
    process_num = 1
    for i in range(process_num):
        p = multiprocessing.Process(target=task, args=(i, game//process_num))
        p.start()
        tasks.append(p)
    for p in tasks:
        p.join()
    print("end", time.time() - start)