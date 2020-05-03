from config import cfg
from twisted.internet import reactor, endpoints
from network.protocols import GameFactory
import threading
import sys

port = str(cfg["server"]["port"])
if len(sys.argv) > 1:
    port = sys.argv[1]
factory = GameFactory()
t = threading.Thread(target=factory.start)
t.setDaemon(True)
t.start()

endpoints.serverFromString(reactor, "tcp:" + port).listen(factory)
reactor.run()
