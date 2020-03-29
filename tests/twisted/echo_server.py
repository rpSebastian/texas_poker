from twisted.internet import protocol, reactor, endpoints
from twisted.protocols.basic import IntNStringReceiver


class Echo(IntNStringReceiver):
    def dataReceived(self, data):
        print(data)
        self.transport.write(data)

    def connectionLost(self, reason):
        print(reason)


class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()


endpoints.serverFromString(reactor, "tcp:1234").listen(EchoFactory())
reactor.run()