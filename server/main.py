from agent.callagent import CallAgentListener
from agent.randomagent import RandomAgentListener
from agent.allinagent import AllinAgentListener
from agent.ruleagent import RuleAgentListener
from twisted.internet import reactor, endpoints
from network.protocols import GameFactory
import better_exceptions
import signal
import random


better_exceptions.MAX_LENGTH = None
signal.signal(signal.SIGCHLD, signal.SIG_IGN)
random.seed(0)
CallAgentListener().start()
RandomAgentListener().start()
AllinAgentListener().start()
RuleAgentListener().start()
endpoints.serverFromString(reactor, "tcp:18888").listen(GameFactory())
reactor.run()
