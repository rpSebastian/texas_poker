import selectors
from logs import logger


class People():
    def __init__(self, sock, name=None):
        self.sock = sock
        self.name = name
        self.session = 0
        self.times = 0

    def update_session(self, money):
        self.times += 1
        self.session += money

    def print_session(self):
        print(f'{self.name} : {self.session} after {self.times} matchs, {self.session * 10 / self.times} mbb/g')


class Room():
    def __init__(self, room_number, room_id):
        self.clients = []
        self.observers = []
        self.room_number = room_number
        self.room_id = room_id
        self.notify_bot_flag = False

    def add_client(self, sock, name):
        self.clients.append(People(sock=sock, name=name))

    def add_observer(self, sock):
        self.observers.append(People(sock=sock))

    def remove_observer(self, sock):
        for observer in self.observers:
            if observer.sock == sock:
                self.observers.remove(observer)
                break

    def full(self):
        return len(self.clients) == self.room_number

    def handle(self):
        raise NotImplementedError()
