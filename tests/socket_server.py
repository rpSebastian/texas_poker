import struct
import socketserver
import time

class MyTCPHandler(socketserver.BaseRequestHandler):
    
    def handle(self):
        try:
            self.main()
        except Exception as e:
            print(self.client_address,"disconnect.")
        finally:
            self.request.close()
    
    def setup(self):
        print("Setup connection:", self.client_address)
    
    def finish(self):
        print("finish run.")

    def main(self):
        # while True:
        #     l = struct.unpack('i', self.request.recv(4))[0]
        #     data = self.request.recv(l).decode()
        #     data = data.upper()
        #     self.request.send(struct.pack('i', len(data.encode())))
        #     self.request.sendall(data.encode())
        l = struct.unpack('i', self.request.recv(4))[0]
        data = self.request.recv(l).decode()
        data = "Hello World py"
        self.request.send(struct.pack('i', len(data.encode())))
        self.request.sendall(data.encode())
        
HOST, PORT = "127.0.0.1", 19999
server=socketserver.ThreadingTCPServer((HOST,PORT),MyTCPHandler)
server.serve_forever()