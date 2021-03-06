import socket
import json
import threading
import time
import json
import struct 
import yaml
import random
import multiprocessing

myip = "127.0.0.1"
# myip = "poker.xuhang.ink"
myport = 18888

def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data)))
    request.sendall(data)
  

def recvJson(request):
    l = struct.unpack('i', request.recv(4))[0]
    data = json.loads(request.recv(l).decode())
    return data
        
class Client(multiprocessing.Process):
    def __init__(self, room_id, name, room_number, bots):
        multiprocessing.Process.__init__(self)
        message = dict(info='connect', room_id=room_id, name=name, room_number=room_number, bots=bots)
        self.info = message 
                
    def run(self):
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        client.connect((myip, myport)) 
        sendJson(client, self.info) 
        data = recvJson(client)
        sendJson(client, {'info': 'start'})
        cnt = 0
        while True:
            data = recvJson(client)
            if data['info'] == 'state' and data['position'] == data['action_position']:
                action = random.choice(data['legal_actions'])
                if action == 'raise':
                    action = 'r' + str(random.randint(data['raise_range'][0], data['raise_range'][1]))
                sendJson(client, {'action': action, 'info': 'action'})
            if data['info'] == 'result':
                print(data)
                cnt += 1
                sendJson(client, {'info': 'start'})
        client.close()

if __name__=="__main__":
    import time
    start = time.time()
    num = 1
    processes = []
    for i in range(num):
        client = Client(42553, 'Bot4', 2, ['RuleAgent'])
        client.start()
        processes.append(client)
 