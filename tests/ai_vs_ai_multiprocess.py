import json
import struct
import socket
from multiprocessing import Process
server_ip = "127.0.0.1"
server_port = 18888
room_id = 121
room_number = 2
bots = ["CallAgent", "CallAgent"]
game_number = 50


def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data)))
    request.sendall(data)


def recvJson(request):
    length = struct.unpack('i', request.recv(4))[0]
    data = json.loads(request.recv(length).decode())
    return data


class Test(Process):
    def __init__(self, room_id):
        super().__init__()
        self.room_id = room_id

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip, server_port))
        message = dict(info='ai_vs_ai', room_id=room_id, room_number=2, bots=bots, game_number=game_number)
        sendJson(client, message)
        while True:
            data = recvJson(client)
            # print(datsa)
            if data["info"] == "error":
                break
        client.close()


if __name__ == "__main__":
    for i in range(100):
        Test(i).start()
