import yaml
import socket
import multiprocessing

with open("./config/config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)


class Listener(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)

    def create_queue(self):
        self.q = multiprocessing.Queue()
        return self.q

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((cfg["server"]["host"], cfg["server"]["port"]))
        server.listen(32767)
        while True:
            client, addr = server.accept()
            self.q.put((client, addr))
