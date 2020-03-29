from myReceiver import JsonReceiver
from twisted.internet import protocol, reactor, endpoints


class Echo(JsonReceiver):
    def jsonReceived(self, data):
        self.sendJson(data)


class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()


endpoints.serverFromString(reactor, "tcp:1234").listen(EchoFactory())
reactor.run()
