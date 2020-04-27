import socket
from config import cfg
from utils import sendJson
from err import RoomFullException, RoomNotExistException, DisconnectException
from room import NoLimitHoldemRoom
from database.mysql import Mysql


class RoomManager():
    def __init__(self):
        self.rooms = {}
        self.mysql = Mysql()

    def create_room(self, room_id, room_number, game_number):
        if room_id not in self.rooms:
            self.rooms[room_id] = NoLimitHoldemRoom(room_number, room_id, game_number, self.mysql)

    def add_observer(self, room_id, sock):
        if room_id not in self.rooms:
            sock.sendJson(RoomNotExistException.error_text)
            sock.transport.loseConnection()
        else:
            self.rooms[room_id].add_observer(sock)

    def add_client(self, room_id, sock, name):
        if self.rooms[room_id].full():
            sock.sendJson(RoomFullException.error_text)
            sock.transport.loseConnection()
        self.rooms[room_id].add_client(sock, name)

    def notify_bots(self, room_id, bots):
        room = self.rooms[room_id]
        if room.notify_bot_flag:
            return
        num = 0
        for bot in bots:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if bot not in cfg["bot"]:
                bot = "CallAgent"
            client.connect((cfg["bot"][bot]["host"], cfg["bot"][bot]["port"]))
            sendJson(client, [room_id, room.room_number, bot+str(num), room.game_number])
            client.close()
            num += 1
        room.notify_bot_flag = True

    def check_start(self, room_id):
        room = self.rooms[room_id]
        if room.full():
            room.init_game()

    def handle(self, room_id, sock, data):
        room = self.rooms[room_id]
        room.handle(sock, data)

    def handle_lost(self, room_id, sock):
        if sock.identity == 'player':
            if room_id in self.rooms:
                room = self.rooms[room_id]
                for client in (*room.clients, *room.observers):
                    client.sock.sendJson(DisconnectException.error_text)
                    client.sock.transport.loseConnection()
                del self.rooms[room_id]
        elif sock.identity == 'observer':
            if room_id in self.rooms:
                room = self.rooms[room_id]
                room.remove_observer(sock)