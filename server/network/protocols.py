from twisted.internet import protocol
from network.base import JsonReceiver
from operator import itemgetter
from room import RoomManager
from logs import logger


class GameProtocol(JsonReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.game = None
        self.room = None
        self.identity = None

    def jsonReceived(self, data):
        info = data["info"]
        peer = self.transport.getPeer()
        if info == "connect":
            logger.info("recv client from {}, {}: {}", peer.host, peer.port, data)
            self.handle_player(data)
        elif info == "observer":
            logger.info("recv client from {}, {}: {}", peer.host, peer.port, data)
            self.handle_observer(data)
        elif info == "ai_vs_ai":
            self.handle_ai_vs_ai(data)
        else:
            self.factory.room_manager.handle(self.room_id, self, data)

    def connectionLost(self, reason):
        self.factory.room_manager.handle_lost(self.room_id, self)

    def handle_observer(self, data):
        self.identity = 'observer'
        room_id = data['room_id']
        self.room_id = room_id
        self.factory.room_manager.add_observer(room_id, self)

    def handle_player(self, data):
        self.identity = 'player'
        room_id, name, room_number, bots = itemgetter('room_id', 'name', 'room_number', 'bots')(data)
        self.room_id = room_id
        self.factory.room_manager.create_room(room_id, room_number)
        self.factory.room_manager.add_client(room_id, self, name)
        self.factory.room_manager.notify_bots(room_id, bots)
        self.factory.room_manager.check_start(room_id)

    def handle_ai_vs_ai(self, data):
        room_id, room_number, bots = itemgetter('room_id', 'room_number', 'bots')(data)
        self.factory.room_manager.create_room(room_id, room_number)
        self.factory.room_manager.notify_bots(room_id, bots)
        self.handle_observer(data)


class GameFactory(protocol.Factory):
    def __init__(self):
        self.room_manager = RoomManager()

    def buildProtocol(self, addr):
        return GameProtocol(self)
