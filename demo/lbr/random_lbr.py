import socket
import json
import threading
import time
import json
import struct 
import yaml
import multiprocessing
import random
myip = "a.xuhang.ink"
myport = 18888

def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data)))
    result = request.sendall(data)

def recvJson(request):
    l = struct.unpack('i', request.recv(4))[0]
    data = json.loads(request.recv(l).decode())
    return data
        
class Client(multiprocessing.Process):
    def __init__(self, name, method=None):
        multiprocessing.Process.__init__(self)
        message = dict(info='lbr', name=name, method=method)
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
                #        if 'raise' in data['legal_actions']:
                #     data['legal_actions'].remove('raise')
                #     for i in range(data['raise_range'][0], data['raise_range'][1]):
                #         data['legal_actions'].append('r'+str(i))
                #     action = random.choice(data['legal_actions'])
                # strategy = [1 for i in range(1326)]
                action = random.choice(data['legal_actions'])
                if action == 'raise':
                    action = 'r' + str(random.randint(data['raise_range'][0], data['raise_range'][1]))
                strategy = [1 for i in range(1326)]
                sendJson(client, {'action': action, 'info': 'action', 'strategy': strategy})
            if data['info'] == 'fold_strategy':
                strategy = [1 / len(data['legal_actions']) for i in range(1326)]
                sendJson(client, {'action': 'fold', 'info': 'action', 'strategy': strategy})    
            if data['info'] == 'result':
                # print(data)
                cnt += 1
                # break
                sendJson(client, {'info': 'start'})
        client.close()

if __name__=="__main__":
    import time
    num = 50
    for i in range(num):
        client = Client('TestRandom', 'lbr-fc-1-4')
        client.start()
    for i in range(num):
        client = Client('TestRandom', 'lbr-fc-3-4')
        client.start()
    for i in range(num):
        client = Client('TestRandom', 'lbr-fcpa-1-4')
        client.start()
    for i in range(num):
        client = Client('TestRandom', 'lbr-fcpa-3-4')
        client.start()
    
