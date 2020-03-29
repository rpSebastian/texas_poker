import socket
import json
import time
import struct
import multiprocessing

myip = "poker.xuhang.ink"
myport = 18888


def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data)))
    request.sendall(data)


def recvJson(request):
    length = struct.unpack('i', request.recv(4))[0]
    data = json.loads(request.recv(length).decode())
    return data


class Client(multiprocessing.Process):
    def __init__(self, room_id, name, room_number, bots):
        multiprocessing.Process.__init__(self)
        message = dict(info='connect', room_id=room_id, name=name, room_number=room_number, bots=bots)
        self.info = message

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((myip, myport))
        sendJson(client, self.info)
        data = recvJson(client)
        sendJson(client, {'info': 'start'})
        cnt = 0
        while True:
            data = recvJson(client)
            if data['info'] == 'state' and data['position'] == data['action_position']:
                if 'call' in data['legal_actions']:
                    action = 'call'
                else:
                    action = 'check'
                sendJson(client, {'action': action, 'info': 'action'})
            if data['info'] == 'result':
                print(data)
                cnt += 1
                if cnt == 100:
                    break
                sendJson(client, {'info': 'start'})
        client.close()


if __name__ == "__main__":
    start = time.time()
    num = 1
    processes = []
    for i in range(num):
        client = Client(42553, 'Bot4', 2, ['CallAgent'])
        client.start()
        processes.append(client)
    for process in processes:
        process.join()
    print(time.time() - start)
