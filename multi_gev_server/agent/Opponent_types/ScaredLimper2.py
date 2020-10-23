# SL 只有拿到最顶级的牌才call，否则对于任何bet都fold
# The Scared Limper always calls the big blind when being the small blind and folds
# to almost any raise at any stage of the game unless holding top hands (i.e. winning
# probability close to one). 

import sys
import os
#os.chdir('..')
# sys.path.append( os.path.join(os.getcwd(),'src') )
import json
import struct
import socket
import random
import numpy as np

# from TerminalEquity.terminal_equity import TerminalEquity
# from Game.card_to_string_conversion import card_to_string
# from Game.card_tools import card_tools

from CardEvaluator.lookup import Lookup

server_ip = "holdem.ia.ac.cn"           # 德州扑克平台地址
server_port = 18888                     # 德州扑克平台开放端口
room_id = int(sys.argv[1])              # 进行对战的房间号
room_number = int(sys.argv[2])          # 一局游戏人数
name = sys.argv[3]                      # 当前程序的 AI 名字
game_number = int(sys.argv[4])          # 最大对局数量
bots = sys.argv[5:] if len(sys.argv) > 5 else []   # 需要系统额外添加的智能体名字

hand_strength_band = 200     # 用于调整手牌阈值



def get_action(data, hand_strength):

    # 'action_history': [
    #                     [{'position': 0, 'action': 'call', 'timestamp': '2020-08-31 18:53:46.810'},
    #                     {'position': 1, 'action': 'check', 'timestamp': '2020-08-31 18:53:46.854'}], 
                        
    #                     [{'position': 1, 'action': 'check', 'timestamp': '2020-08-31 18:54:09.930'}, 
    #                     {'position': 0, 'action': 'check', 'timestamp': '2020-08-31 18:54:09.974'}], 

    #                     [{'position': 1, 'action': 'check', 'timestamp': '2020-08-31 18:54:10.982'}, 
    #                     {'position': 0, 'action': 'check', 'timestamp': '2020-08-31 18:54:11.026'}], 
                        
    #                     [{'position': 1, 'action': 'check', 'timestamp': '2020-08-31 18:54:11.106'}, 
    #                     {'position': 0, 'action': 'check', 'timestamp': '2020-08-31 18:54:11.150'}]
    #                     ]
    
    # 小盲时，直接call
    if (data["action_history"][0] == []) and (data["position"] == 0) and ('call' in data['legal_actions']):
        return 'call'

    # 当对手raise时候，判断自己牌力大小做动作
    #print(data['action_history'], len(data["action_history"]))
    if data['action_history'][-1] == []:
        opponent_last_action = data['action_history'][-2][-1]['action']
    else: 
        opponent_last_action = data['action_history'][-1][-1]['action']
    print("opponent_action:",opponent_last_action)
    if (opponent_last_action[0] == 'r') & (hand_strength < hand_strength_band):
        return 'fold'

    if 'call' in data['legal_actions']:
        action = 'call'
    else:
        action = 'check'
    return action





def sendJson(request, jsonData):
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data)))
    request.sendall(data)


def recvJson(request):
    data = request.recv(4)
    length = struct.unpack('i', data)[0]
    data = request.recv(length).decode()
    while len(data) != length:
        data = data + request.recv(length - len(data)).decode()
    data = json.loads(data)
    return data

if __name__ == "__main__":

    lookup = Lookup()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    message = dict(info='connect', room_id=room_id, name=name, room_number=room_number, bots=bots, game_number=game_number)
    sendJson(client, message)
    game_street = 0

    while True:
        data = recvJson(client)

        if data['info'] == 'state':

            if data['position'] == data['action_position']:
                #print(data)
                position = data['position']

                private_card = data['private_card']
                public_card = data['public_card']  

                #print("boards:", public_card, ' private_card:', private_card, ' hand_strength:', hand_strengths[hand_idx])
                
                action = get_action(data, lookup.calc(private_card, public_card))
                #print(action)

                sendJson(client, {'action': action, 'info': 'action'})
        elif data['info'] == 'result':
            print('win money: {},\tyour card: {},\topp card: {},\t\tpublic card: {}'.format(
                data['players'][position]['win_money'], data['player_card'][position], data['player_card'][1 - position], data['public_card'])) 
            sendJson(client, {'info': 'ready', 'status': 'start'})
            print("-----------new-hand--------------")
            #term_eq.set_board(np.zeros([]))
            game_street = 0
        else:
            print(data)
            break
    client.close()
