import socket
import json
import threading
import time
import json
import struct 
import yaml
import multiprocessing

myip = "poker.xuhang.ink"
myport = 18888

def sendJson(request, jsonData):
    try:
        data = json.dumps(jsonData).encode()
        request.send(struct.pack('i', len(data)))
        request.sendall(data)
    except Exception as e:
        print(e)

def recvJson(request):
    try:
        l = struct.unpack('i', request.recv(4))[0]
        data = json.loads(request.recv(l).decode())
        return data
    except Exception as e:
        print(e)

total = multiprocessing.Value("d", 0)

class Client(multiprocessing.Process):
    def __init__(self, room_id, name, room_number, bots):
        multiprocessing.Process.__init__(self)
        message = dict(info='connect', room_id=room_id, name=name, room_number=room_number, bots=bots)
        self.info = message 
                
    def run(self):
        start = time.time()
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        client.connect((myip, myport)) 
        sendJson(client, self.info) 
        data = recvJson(client)
        print(data)
        sendJson(client, {'info': 'start'})
        count = 0
        while True:
            data = recvJson(client)
            print(data)
            if data['info'] == 'state' and data['position'] == data['action_position']:
                if 'call' in data['legal_actions']:
                    action = 'call'
                else:
                    action = 'check'
                sendJson(client, {'action': action, 'info': 'action'})
            if data['info'] == 'result':
                count += 1
                if count == 1000000:
                    break
                sendJson(client, {'info': 'start'})
        end = time.time()
        # client.shutdown(socket.SHUT_RDWR)
        client.close()
        global total
        total.value += end - start

if __name__=="__main__":
    start = time.time()
    num = 1
    processes = []
    for i in range(num):
        client = Client(1, 'Bot', 3, ['RandomAgent', 'CallAgent'])
        client.start()
        processes.append(client)
    for p in processes:
        p.join()
    
    print(total.value / num)
    print(time.time() - start)
