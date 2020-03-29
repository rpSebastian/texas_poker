import time
import random
import requests
import multiprocessing
from utils.utils import sendJson, recvJson
from database.mysql import Mysql

class SlumbotKernel(multiprocessing.Process):
    def __init__(self, name, client, observer_queue):
        super().__init__()
        self.name = name
        self.client = client
        self.url = 'http://www.slumbot.com/cgi-bin/cgi_middleman'
        self.sid = int(time.time() * 1000000 + int(random.random() * 1000000))
        self.under_line = 1574664725
        self.observer_queue = observer_queue
        self.mysql = Mysql()

    def run(self):
        self.work()
        # try:
        #     self.work()
        # except Exception as e:
        #     print(e)
        #     self.mysql.end()
    
    def work(self):
        # self.login()
        self.notify_name(0)
        while True:
            self.recv_start()
            data = self.slumbot_send_action('nh')
            is_terminal = self.parse_data(data)
            while not is_terminal:
                self.notify_state()
                message = recvJson(self.client)
                action = message['action']
                # action = 'call'
                data = self.slumbot_send_action(action)
                is_terminal = self.parse_data(data)
            self.notify_result()
            self.save_data(data)
    
    def save_data(self, data):
        state = {}
        state['public_card'] = self.parse_board(data["board"])
        state['action_history'] = self.parse_action_history(data)
        state['name'] = [0, 0]
        state['name'][self.position] = self.name
        state['name'][1 - self.position] = 'slumbot'
        state['position'] = [0, 1]
        state['player_card'] = [0, 0]
        state['player_card'][self.position] = self.private_card
        state['player_card'][1 - self.position] = self.oppnent_private_card
        state['win_money'] = self.win_money
        self.mysql.save(state)

    def parse_data(self, data):
        self.action_history = self.parse_action_history(data)
        self.position = 1 - data['p1']
        self.private_card = self.parse_board(data["holes"])
        self.public_card = self.parse_board(data["board"])
        self.get_last_action_player(self.action_history)
        if self.last_action_player == 1 - self.position:
            self.notify_opponent_state()
        if 'outcome' in data:
            is_terminal = True
            self.notify_last_state()
            self.parse_result_data(data)
        else:
            is_terminal = False 
            self.parse_match_data(data)
        # if is_terminal:
        #     print(data)
        return is_terminal 
    
    def parse_result_data(self, data):
        self.oppnent_private_card = self.parse_board(data["oppholes"])
        if 'fold' in self.action_history[-1]:
            self.player_card = [[], []]
        else:
            self.player_card = [0, 0]
            self.player_card[self.position] = self.private_card
            self.player_card[1 - self.position] = self.oppnent_private_card
        self.win_money = [0, 0]
        if data['outcome'] == 0:
            self.win_money[self.position] = 0
        elif data['outcome'] > 0:
            self.win_money[self.position] = data['ps'] / 2 + data['oppb']
        else:
            self.win_money[self.position] = -(data['ps'] / 2 + data['ourb'])
        self.win_money[1 - self.position] = -self.win_money[self.position]
        
    def notify_last_state(self):
        state = {}
        state['info'] = 'state'
        state['position'] = self.position
        state['action_position'] = -1
        state['private_card'] = self.private_card
        state['public_card'] = self.public_card
        state['action_history'] = self.action_history
        sendJson(self.client, state)

    def notify_opponent_state(self):
        import copy
        state = {}
        state['info'] = 'state'
        state['position'] = self.position
        state['action_position'] = 1 - self.position
        state['private_card'] = self.private_card
        state['public_card'] = self.public_card
        action_history = copy.deepcopy(self.action_history)
        if self.last_action_player == -1:
            state['action_history'] = action_history
            sendJson(self.client, state)
        else:
            messages = []
            while self.last_action_player == 1 - self.position:
                if len(action_history[-1]) == 0:
                    action_history.pop()
                action_history[-1].pop()
                state['action_history'] = action_history
                self.get_last_action_player(action_history)
                messages.append(copy.deepcopy(state))
            for message in reversed(messages):
                sendJson(self.client, message)
        
    def get_last_action_player(self, action_history):
        for round_history in reversed(action_history):
            for action in reversed(round_history):
                p, a = action.split(':')
                self.last_action_player = int(p)    
                return 
        self.last_action_player = -1


    def login(self):
        data = {}
        data['type'] = 'login'
        data['username'] = 'zjcxxh1'
        data['pw'] = '315300'
        data['_'] = self.under_line
        self.under_line += 1
        response = requests.get(self.url, params=data)

    def notify_state(self, last=False):
        state = {}
        state['info'] = 'state'
        state['position'] = self.position
        state['action_position'] = self.position
        state['legal_actions'] = self.legal_actions
        state['raise_range'] = self.raise_range
        state['private_card'] = self.private_card
        state['public_card'] = self.public_card
        state['action_history'] = self.action_history
        sendJson(self.client, state)

    def notify_result(self):
        state = {}
        state['info'] = 'result'
        state['position'] = self.position
        state['win_money'] = self.win_money
        state['player_card'] = self.player_card
        state['public_card'] = self.public_card
        sendJson(self.client, state)

    def parse_match_data(self, data):
        self.raise_range = [int(data['minb']), int(data['maxb'])]
        self.legal_actions = self.get_legal_actions(self.action_history)

    def slumbot_send_action(self, action):
        if action == 'nh':
            self.ai = 0
        if action[0] == 'r':
            action = 'b' + action[1:]
        if action == 'check':
            action = 'k'
        if action == 'call':
            action = 'c'
        if action == 'fold':
            action = 'f'
        data = {}
        data["type"] = "play"
        data["action"] = action
        data["sid"] = self.sid
        data["un"] = self.name
        data["ai"] = self.ai
        data["_"] = self.under_line
        self.under_line += 1
        self.ai += 1
        response = requests.get(self.url, params=data)
        # try:
        #     print(response.json()['action'])
        # except:
        #     print(response.text())
        return response.json()

    def get_legal_actions(self, action_history):
        round_raised = self.get_round_raised(action_history)
        cur_round = len(self.action_history)
        legal_actions = ['fold']
        if round_raised[cur_round - 1] > 0:
            legal_actions.append('call')
        else:
            legal_actions.append('check')
        if sum(round_raised) < 20000:
            legal_actions.append('raise')
        return legal_actions

    def get_round_raised(self, action_history):
        result = []
        for i, one_round in enumerate(action_history):
            rmax = 0
            if i == 0:
                rmax = 100
            for one_action in one_round:
                p, a = one_action.split(":")
                if a[0] == "r":
                    rmax = max(rmax, int(a[1:]))
            result.append(rmax)
        return result 

    def parse_board(self, board):
        cards = []
        for i in range(0, len(board), 2):
            cards.append(board[i:i+2])
        return cards 

    def parse_action_history(self, data):
        action_history = []
        first_player = 0
        for round_actions in data['action'].split('/'):
            cur_player = first_player
            round_history = []
            while round_actions != "":
                action, round_actions = self.read_one_action(round_actions)
                round_history.append(str(cur_player) + ":" + action)
                cur_player = 1 - cur_player
            action_history.append(round_history)
            first_player = 1
        return action_history 

    def read_one_action(self, round_actions):
        if round_actions[0] == "b":
            pointer = 1
            while pointer < len(round_actions) and round_actions[pointer] >= '0' and round_actions[pointer] <= '9':
                pointer += 1
            action = "r" + round_actions[1:pointer]
            round_actions = round_actions[pointer:]  
        elif round_actions[0] == "c":
            action = "call"
            round_actions = round_actions[1:] 
        elif round_actions[0] == "k":
            action = "check"
            round_actions = round_actions[1:] 
        elif round_actions[0] == "f":
            action = "fold"
            round_actions = round_actions[1:] 
        return action, round_actions

    def recv_start(self):
        message = recvJson(self.client)

    def notify_name(self, i):
        message = self.name_message(i)
        sendJson(self.client, message)    

    def name_message(self, i):
        message = {}
        message['info'] = 'name'
        message['name'] = ['slumbot', self.name]
        message['position'] = 1
        return message