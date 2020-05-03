from myReceiver import JsonReceiver
from twisted.internet import protocol, reactor, endpoints
import uuid
import threading


class Echo(JsonReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.uuid = str(uuid.uuid4())
        self.factory.uuids[self.uuid] = self

    def jsonReceived(self, data):
        self.factory.message_queue.append([self.uuid, data])

    def connectionLost(self, reason):
        print('over')
        self.sendJson(['haha'])

class EchoFactory(protocol.Factory):
    def __init__(self):
        self.message_queue = []
        self.uuids = {}

    def buildProtocol(self, addr):
        return Echo(self)

    def listen(self):
        while True:
            if len(self.message_queue) > 0:
                uuid, data = self.message_queue.pop(0)
                self.uuids[uuid].sendJson(data)


factory = EchoFactory()
t = threading.Thread(target=factory.listen)
t.setDaemon(True)
t.start()

endpoints.serverFromString(reactor, "tcp:1234").listen(factory)
reactor.run()
