from connect.listener import Listener
from connect.waiter import Waiter
from agent.callagent import CallAgentListener
from agent.randomagent import RandomAgentListener
from agent.allinagent import AllinAgentListener
from agent.ruleagent import RuleAgentListener
import better_exceptions
better_exceptions.MAX_LENGTH = None
import random
import signal

signal.signal(signal.SIGCHLD,signal.SIG_IGN)

random.seed(0)

listener = Listener()
waiter = Waiter(listener.create_queue())
call_agent_listener = CallAgentListener()
random_agent_listener = RandomAgentListener()
allin_agent_listener = AllinAgentListener()
rule_agent_listener = RuleAgentListener()
listener.start()
waiter.start()
call_agent_listener.start()
random_agent_listener.start()
allin_agent_listener.start()
rule_agent_listener.start()
