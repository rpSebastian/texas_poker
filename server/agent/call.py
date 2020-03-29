from twisted.internet.protocol import ClientFactory
from network.base import JsonReceiver
from config import cfg
from twisted.internet import reactor
from twisted.internet import protocol



class CallServer(JsonReceiver):

    def __init__(self, factory):
        self.factory = factory

    def jsonReceived(self, data):
        room_id, room_number, name = data
        self.transport.loseConnection()
        reactor.connectTCP(cfg['server']['host'], cfg['server']['port'], CallClientFactory())


class CallServerFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return CallServer(self)


class CallClient(JsonReceiver):
    def connectionMade(self):
        message = dict(info='connect', room_id=10, name='test', room_number=2, bots=['CallAgent'])
        self.sendJson(message)

    def jsonReceived(self, data):
        if data['info'] == 'name':
            self.sendJson({'info': 'start'})
        if data['info'] == 'state' and data['position'] == data['action_position']:
            if 'call' in data['legal_actions']:
                action = 'call'
            else:
                action = 'check'
            self.sendJson({'action': action, 'info': 'action'})
        if data['info'] == 'result':
            self.sendJson({'info': 'start'})
            self.num += 1
            if self.num % 5 == 0:
                self.transport.loseConnection()



endpoints.serverFromString(reactor, "tcp:18888").listen(GameFactory())
reactor.run()
reactor.connectTCP(cfg['server']['host'], cfg['server']['port'], CallClientFactory())
reactor.run()

