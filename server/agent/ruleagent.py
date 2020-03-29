import socket
import json
import struct
import multiprocessing
import yaml
from .guize import allturnsmallblindaction, allturnbigblindaction


with open("./config/config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)


def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data)))
    request.sendall(data)


def recvJson(request):
    l = struct.unpack('i', request.recv(4))[0]
    data = json.loads(request.recv(l).decode())
    return data


class RuleAgentListener(multiprocessing.Process):

    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((cfg["bot"]["RuleAgent"]["host"], cfg["bot"]["RuleAgent"]["port"]))
        server.listen(20)
        while True:
            client, addr = server.accept()
            room_id, room_number, name = recvJson(client)
            client.close()
            agent = RuleAgent(room_id, room_number, name)
            agent.start()

class RuleAgent(multiprocessing.Process):
    def __init__(self, room_id, room_number, name):
        multiprocessing.Process.__init__(self)
        message = dict(info='connect', room_id=room_id, name=name, room_number=room_number, bots=[])
        self.info = message 

    def get_action(self, data):
        position = data['position']
        hand = ''.join(data['private_card'])
        board = ''.join(data['public_card'])
        action_history = data['action_history']
        round_raised = self.get_round_raised(data['action_history'])
        my_cur_bet = self.get_current_round_bet(position, action_history)
        opp_cur_bet = self.get_current_round_bet(1-position, action_history)
        opp_bet = opp_cur_bet - my_cur_bet
        bot_bet = sum(round_raised[:-1]) + my_cur_bet
        turn = self.count_turn(data['action_history'], position)
        if position == 0:
            plac = allturnsmallblindaction(hand,board,opp_bet,bot_bet,turn)
        else:
            plac = allturnbigblindaction(hand,board,opp_bet,bot_bet,turn)
        if plac[0] == 'c' or plac == 'r0':
            if 'call' in data['legal_actions']:
                action = 'call'
            else:
                action = 'check'
        elif plac[0] == 'f':
            action = 'fold'
        else:
            amount = int(plac[1:]) + opp_cur_bet
            amount = min(amount, data['raise_range'][1])
            amount = max(amount, data['raise_range'][0])
            action = 'r' + str(amount)
        return action

    def count_turn(self, action_history, position):
        num = 1
        for action in action_history[-1]:
            p, a = action.split(':')
            if position == int(p):
                num += 1
        return num

    def get_current_round_bet(self, position, action_history):
        actions = action_history[-1].copy()
        if len(action_history) == 1:
            actions.insert(0, '1:r100')
            actions.insert(0, '0:r50')
        pmax = None
        for action in reversed(actions):
            p, a = action.split(':')
            if int(p) == position and a[0] == 'r' and pmax is None:
                return int(a[1:])
            if int(p) == position and a[0] == 'c' and pmax is None:
                pmax = 0
            if pmax is not None and a[0]=='r':
                pmax = max(pmax, int(a[1:]))
        if pmax == None:
            pmax = 0
        return pmax

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

    def run(self):
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        client.connect((cfg["server"]["host"], cfg["server"]["port"])) 
        try:
            sendJson(client, self.info) 
            cnt = 0
            while True:
                data = recvJson(client)
                if data['info'] == 'state' and data['position'] == data['action_position']:
                    action = self.get_action(data)
                    sendJson(client, {'action': action, 'info': 'action'})
                    position = data['position']
                if data['info'] == 'result':
                    cnt += 1
                    # if cnt == 100:
                        # break
                    # print(position, data)
                    sendJson(client, {'info': 'ready', 'status': 'start'})
            client.close()
        except Exception as e:
            # print(e)
            pass
        finally:
            client.close()

