class SPlayer():
    def __init__(self, socket, name):
        self.socket = socket
        self.name = name
        self.session = 0
        self.times = 0

    def update_session(self, money):
        self.times += 1
        self.session += money
    
    def print_session(self):
        print(f'{self.name} : {self.session} after {self.times} matchs, {self.session * 10 / self.times} mbb/g')