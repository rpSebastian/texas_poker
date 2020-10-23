from agent_base import Agent
import random


class CallAgent(Agent):
    def get_action(self, data):
        if 'call' in data['legal_actions']:
            action = 'call'
        else:
            action = 'check'
        return action


class RandomAgent(Agent):
    def get_action(self, data):
        if 'fold' in data['legal_actions']:
            data['legal_actions'].remove('fold')
        choose_index = random.randint(0, len(data['legal_actions']) - 1)
        if data['legal_actions'][choose_index] == 'raise':
            action = 'r' + str(random.randint(data['raise_range'][0], data['raise_range'][1]))
        else:
            action = data['legal_actions'][choose_index]
        return action


class AllinAgent(Agent):
    def get_action(self, data):
        action = 'r' + str(data['raise_range'][1])
        return action


class FoldAgent(Agent):
    def get_action(self, data):
        action = "fold"
        return action
    

if __name__ == "__main__":
    agent = CallAgent(1000000, 2, "CallAgent", 2, "holdem.ia.ac.cn", 18888, ["CallAgent"], verbose=True)
    agent.run()