from config import cfg
from twisted.internet import reactor, endpoints
from network.protocols import GameFactory
import threading

factory = GameFactory()
t = threading.Thread(target=factory.start)
t.setDaemon(True)
t.start()

endpoints.serverFromString(reactor, "tcp:" + str(cfg["server"]["port"])).listen(factory)
reactor.run()
