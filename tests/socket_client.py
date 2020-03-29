import socket
import json
import time
import struct
import threading
class Client(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        client.connect(('127.0.0.1', 19999)) 
        for i in range(10):
            data = "Hello world"
            client.send(struct.pack('i', len(data.encode())))
            client.sendall(data.encode())
            l = struct.unpack('i', client.recv(4))[0]
            data = client.recv(l).decode()
            print(data)
        client.close()

if __name__=="__main__":
    for i in range(1):
        client = Client()
        client.start()