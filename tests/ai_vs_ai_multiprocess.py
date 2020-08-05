import json
import struct
import socket
import traceback

import gevent
import gevent.monkey 
gevent.monkey.patch_all()

server_ip = "holdem.ia.ac.cn"
server_port = 18888
bots = ["CallAgent", "RandomAgent"]
game_number = 4
game = 1

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
        message = dict(info='ai_vs_ai', room_id=self.room_id, room_number=2, bots=bots, game_number=game_number)
        sendJson(client, message)
        num = 0
        if self.xid != 0:
            client.close()
            return
        try:
            while True:
                data = recvJson(client)
                if data["info"] == "state":
                    pass
                elif data['info'] == 'result':
                    num += 1
                else:
                    # print(data)
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
        p = Test(i+123456, i)
        tasks.append(gevent.spawn(p.run))
    gevent.joinall(tasks)
    print("game: {} game_number:{} time:{}".format(game, game_number, time.time() - start))
    
