import json
import struct
import socket
import traceback
from multiprocessing import Process
server_ip = "172.18.40.65"
server_port = 18888
bots = ["CallAgent", "OpenStack"]
game_number = 10


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


class Test(Process):
    def __init__(self, room_id):
        super().__init__()
        self.room_id = room_id

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip, server_port))
        message = dict(info='ai_vs_ai', room_id=self.room_id, room_number=2, bots=bots, game_number=game_number)
        sendJson(client, message)
        num = 0
        try:
            while True:
                data = recvJson(client)
                if data['info'] == 'result':
                    num += 1
        except Exception as e:
            if num != game_number:
                print(num, e)
        client.close()


if __name__ == "__main__":
    import time
    start = time.time()
    process = []
    num = 4
    for i in range(num):
        p = Test(i+100000)
        p.start()
        process.append(p)
    for p in process:
        p.join()
    end = time.time()
    print(num, game_number, end - start)

