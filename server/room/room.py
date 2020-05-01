import selectors
from logs import logger


class Room():
    def __init__(self, room_manager, clients, room_id, room_number, game_number, mysql):
        self.clients = clients
        self.room_number = room_number
        self.game_number = game_number
        self.room_id = room_id
        self.mysql = mysql
        self.room_manager = room_manager

    def handle(self):
        raise NotImplementedError()
