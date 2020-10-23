import time
import json
import struct
import socket
import datetime
import random
import numpy as np

import gevent
import gevent.monkey 
gevent.monkey.patch_all()

import argparse
from multiprocessing import Process

parser = argparse.ArgumentParser(description="同时发起n场对战，每场对战进行m局")
parser.add_argument("--server_ip", type=str, default="holdem.ia.ac.cn", help="德扑服务器地址")
parser.add_argument("--server_port", type=int, default=18888, help="德扑服务器端口")
parser.add_argument("--num_players", type=int, default=2, help="对战人数, 2/6", choices=[2, 6])
parser.add_argument("--connections", type=int, default=1, help="同时发起的对战数")
parser.add_argument("--num_matches", type=int, default=1, help="每场对战进行的局数" )
parser.add_argument("--verbose", action="store_true", help="是否打印接收到的数据" )

args = parser.parse_args()
args.bots = ["CallAgent" for i in range(args.num_players)]

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

class Test():
    def __init__(self, room_id, room_number, bots, game_number):
        super().__init__()
        self.room_id = room_id
        self.room_number = room_number
        self.bots = bots
        self.game_number = game_number

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((args.server_ip, args.server_port))
        message = dict(info='ai_vs_ai', room_id=self.room_id, room_number=self.room_number, bots=self.bots, game_number=self.game_number)
        sendJson(client, message)
        while True:
            data = recvJson(client)
            if args.verbose:
                print(data)
            if data["info"] == "state":
                pass
            elif data['info'] == 'result':
                pass
            else:
                if data["info"] != "success":
                    print(data)
                break
        client.close()

def battle(connections):
    tasks = []
    start_room_id = random.randint(2000000, 3000000)
    for i in range(int(connections)):
        p = Test(start_room_id + i, args.num_players, args.bots, args.num_matches)
        tasks.append(gevent.spawn(p.run))
    gevent.joinall(tasks)

if __name__ == "__main__":
    t = lambda: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    start = time.time()
    print("Start playing at {}".format(t()))
    print("{} Connections, {} Matches {} Players each connection".format(args.connections, args.num_matches, args.num_players))

    battle(args.connections)
    
    print("End playing at {}".format(t()))
    print("Use time: {:.6f}s".format(time.time() - start))
