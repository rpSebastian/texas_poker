import context
from agent.callagent import CallAgentListener
from agent.randomagent import RandomAgentListener
from agent.allinagent import AllinAgentListener
from agent.ruleagent import RuleAgentListener

CallAgentListener().start()
RandomAgentListener().start()
AllinAgentListener().start()
RuleAgentListener().start()
