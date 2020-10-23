import json
import struct
import socket
import traceback
import time

import gevent
import gevent.monkey 
gevent.monkey.patch_all()

server_ip = "holdem.ia.ac.cn"
server_port = 18888
room_number = 2
bots = ['CallAgent', 'CallAgent']
game_number = 2
game = 30

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
    def __init__(self, room_id, xid):
        super().__init__()
        self.room_id = room_id
        self.xid = xid

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip, server_port))
        message = dict(info='ai_vs_ai', room_id=self.room_id, room_number=room_number, bots=bots, game_number=game_number)
        sendJson(client, message)
        s = time.time()
        start = None
        num = 0
        # if self.xid != 0:
        #     client.close()
        #     return
        try:
            while True:
                data = recvJson(client)
                if start is None:
                    # print(time.time() - s)
                    start = time.time()
                if data["info"] == "state":
                    pass
                elif data['info'] == 'result':
                    # print(time.time() - start)
                    start = time.time()
                    num += 1
                else:
                    print(data)
                    break
        except Exception as e:
            if num != game_number:
                print(num, e)
        client.close()


if __name__ == "__main__":
    import time
    start = time.time()
    tasks = []
    for i in range(game):
        p = Test(i+700001, i)
        tasks.append(gevent.spawn(p.run))
    gevent.joinall(tasks)
    print("game: {} game_number:{} time:{}".format(game, game_number, time.time() - start))
    
