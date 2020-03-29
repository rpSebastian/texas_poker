import socket
import json
import threading
import time
import json
import struct 
import yaml
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
    def __init__(self, name, method=None):
        multiprocessing.Process.__init__(self)
        message = dict(info='lbr', name=name,  method=method)
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
                if 'call' in data['legal_actions']:
                    action = 'call'
                else:
                    action = 'check'
                strategy = [1 for i in range(1326)]
                sendJson(client, {'action': action, 'info': 'action', 'strategy': strategy})
            if data['info'] == 'fold_strategy':
                strategy = [0 for i in range(1326)]
                sendJson(client, {'action': 'fold', 'info': 'action', 'strategy': strategy})    
            if data['info'] == 'result':
                print(data)
                cnt += 1
                sendJson(client, {'info': 'start'})
        client.close()

if __name__=="__main__":
    import time
    num = 1
    for i in range(num):
        client = Client('TestCall', 'lbr-fc-1-4')
        client.start()
    for i in range(num):
        client = Client('TestCall', 'lbr-fc-3-4')
        client.start()
    for i in range(num):
        client = Client('TestCall', 'lbr-fcpa-1-4')
        client.start()
    for i in range(num):
        client = Client('TestCall', 'lbr-fcpa-3-4')
        client.start()
