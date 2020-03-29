from twisted.internet.protocol import ClientFactory
from network.base import JsonReceiver
from config import cfg
from twisted.internet import reactor


class CallClient(JsonReceiver):
    def connectionMade(self):
        # print(2)
        message = dict(info='connect', room_id=10, name='test', room_number=2, bots=['CallAgent'])
        self.sendJson(message)
        self.num = 0

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
                reactor.connectTCP(cfg['server']['host'], cfg['server']['port'], CallClientFactory())

class CallClientFactory(ClientFactory):
    def buildProtocol(self, addr):
        return CallClient()


reactor.connectTCP(cfg['server']['host'], cfg['server']['port'], CallClientFactory())
reactor.run()

