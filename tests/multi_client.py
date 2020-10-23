import json
import struct
import socket
import time

import gevent
from gevent import monkey
gevent.monkey.patch_all()

server_ip = "holdem.ia.ac.cn"
server_port = 5000
room_id = 1000002
room_number = 2
game_number = 2
bots = ["TightPassive"]
name = "CallAgent"

batch_num = 1

def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data))+data)


def recvJson(request):
    length = struct.unpack('i', request.recv(4))[0]
    data = json.loads(request.recv(length).decode())
    return data

class Game():
    
    def __init__(self, room_id, name, room_number, bots, game_number):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((server_ip, server_port))
        self.message = dict(info='connect', room_id=room_id, name=name, room_number=room_number, bots=bots, game_number=game_number)
    
    def run(self):
        sendJson(self.client, self.message)
        num = 0
        while True:
            data = recvJson(self.client)
            print(data)
            if 'position' in data:
                position = data['position']
            if data['info'] == 'state':
                if data['position'] == data['action_position']:
                    if 'call' in data['legal_actions']:
                        action = 'call'
                    else:
                        action = 'check'
                    sendJson(self.client, {'action': action, 'info': 'action'})
            elif data['info'] == 'result':
                num += 1
                sendJson(self.client, {'info': 'ready', 'status': 'start'})
            else:
                print(data)
                break
        

if __name__ == "__main__":
    games = []
    for i in range(batch_num):
        game = Game(room_id, name, room_number, bots, game_number)
        games.append(game)
    gevent.joinall([
        gevent.spawn(game.run) 
        for game in games
    ])

    