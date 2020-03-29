import socket
import json
import threading
import time
import json
import struct 
import yaml
import multiprocessing

myip = "127.0.0.1"
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
    def __init__(self, name):
        multiprocessing.Process.__init__(self)
        message = dict(info='lbr', name=name)
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
                strategy = [1 for i in range(1326)]
                sendJson(client, {'action': 'fold', 'info': 'action', 'strategy': strategy})
            if data['info'] == 'fold_strategy':
                strategy = [1 for i in range(1326)]
                sendJson(client, {'action': 'fold', 'info': 'action', 'strategy': strategy})    
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
        client = Client('fold')
        client.start()
        processes.append(client)
    for process in processes:
        process.join()
    print(time.time() - start)