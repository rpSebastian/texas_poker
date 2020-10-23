# LP 对于大部分牌都call，弱牌fold, 很少raise

import sys
import os
#os.chdir('..')
# sys.path.append( os.path.join(os.getcwd(),'src') )
import json
import struct
import socket
import random
import numpy as np

from CardEvaluator.lookup import Lookup

server_ip = "holdem.ia.ac.cn"           # 德州扑克平台地址
server_port = 18888                     # 德州扑克平台开放端口
room_id = int(sys.argv[1])              # 进行对战的房间号
room_number = int(sys.argv[2])          # 一局游戏人数
name = sys.argv[3]                      # 当前程序的 AI 名字
game_number = int(sys.argv[4])          # 最大对局数量
bots = sys.argv[5:] if len(sys.argv) > 5 else []   # 需要系统额外添加的智能体名字

# 用于调整手牌阈值 
# [-663, low] --> fold
# [low, high] --> call/check
# [high, 663] --> rasie 0.25-1 pot
hand_strength_band_high = 500     
hand_strength_band_low = -300

def clip_pot(a, cl, ch):
    if a < cl:
        return cl
    if a > ch:
        return ch
    return a

def get_action(data, last_round_raise, hand_strength):

    if hand_strength < hand_strength_band_low & ('fold' in data['legal_actions']):
        return 'fold'

    elif hand_strength < hand_strength_band_high:
        if 'call' in data['legal_actions']:
            return 'call'
        else:
            return 'check'
    elif hand_strength > hand_strength_band_high:
        if 'raise' in data['legal_actions']:
            self_position = data['position']
            raise_range_low, raise_range_high = data['raise_range']

            self_pot = data['players'][self_position]['total_money'] - data['players'][self_position]['money_left']
            opponent_pot = data['players'][1 - self_position]['total_money'] - data['players'][1 - self_position]['money_left']
            pot = [max(self_pot, opponent_pot) //2, max(self_pot, opponent_pot) * 2]
            
            raise_number = opponent_pot + random.randrange(pot[0], pot[1]) - last_round_raise
            
            raise_nums = clip_pot(raise_number, raise_range_low, raise_range_high)
            print(self_pot, opponent_pot, pot, raise_nums, raise_range_low, raise_range_high)
            
            return 'r' + str(raise_nums)
        elif 'call' in data['legal_actions']:
            return 'call'
        else:
            return 'check'
    else:
        if 'call' in data['legal_actions']:
            return 'call'
        else:
            return 'check'




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
    last_round_raise = 0

    while True:
        data = recvJson(client)
        #print(data)

        if data['info'] == 'state':

            if data['position'] == data['action_position']:
                #print(data)
                position = data['position']

                private_card = data['private_card']
                public_card = data['public_card']  
                #print("boards:", public_card, '   private_card:', private_card)
                if len(public_card) > game_street:
                    game_street = len(public_card)
                    last_round_raise = data['players'][position]['total_money'] - data['players'][position]['money_left']

                #print("boards:", public_card, ' private_card:', private_card, ' hand_strength:', hand_strengths[hand_idx])
                
                action = get_action(data, last_round_raise, lookup.calc(private_card, public_card))
                #print(action)

                sendJson(client, {'action': action, 'info': 'action'})
        elif data['info'] == 'result':
            print('win money: {},\tyour card: {},\topp card: {},\t\tpublic card: {}'.format(
                data['players'][position]['win_money'], data['player_card'][position], data['player_card'][1 - position], data['public_card'])) 
            sendJson(client, {'info': 'ready', 'status': 'start'})
            print("-----------new-hand--------------")
            game_street = 0
            last_round_raise = 0
        else:
            print(data)
            break
    client.close()
