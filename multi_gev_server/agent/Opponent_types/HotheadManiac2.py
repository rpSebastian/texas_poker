# HM  总是随机raise 0.5/1 pot
# pot：当前桌面总筹码量

import sys
import json
import struct
import socket
import random

server_ip = "holdem.ia.ac.cn"           # 德州扑克平台地址
server_port = 18888                     # 德州扑克平台开放端口
room_id = int(sys.argv[1])              # 进行对战的房间号
room_number = int(sys.argv[2])          # 一局游戏人数
name = sys.argv[3]                      # 当前程序的 AI 名字
game_number = int(sys.argv[4])          # 最大对局数量
bots = sys.argv[5:] if len(sys.argv) > 5 else []   # 需要系统额外添加的智能体名字



def get_action(data, last_round_raise):
    self_position = data['position']
    #print(data)
    if 'raise' in data['legal_actions']:
        #action = 'r'
        raise_range_low, raise_range_high = data['raise_range']

        self_pot = data['players'][self_position]['total_money'] - data['players'][self_position]['money_left']
        opponent_pot = data['players'][1 - self_position]['total_money'] - data['players'][1 - self_position]['money_left']
        pot = [2 * max(self_pot, opponent_pot), max(self_pot, opponent_pot)]

        raise_number = opponent_pot + pot[random.randint(0, 1)] - last_round_raise
        raise_nums = clip_pot(raise_number, raise_range_low, raise_range_high)
        
        action = 'r' + str(raise_nums)
        #print(self_pot, opponent_pot, pot, raise_nums, action, raise_range_low, raise_range_high)
    elif 'call' in data['legal_actions']:
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
                position = data['position']

                public_card = data['public_card']
                if len(public_card) > game_street:
                    game_street = len(public_card)
                    last_round_raise = data['players'][position]['total_money'] - data['players'][position]['money_left']
                    

                action = get_action(data, last_round_raise)
                sendJson(client, {'action': action, 'info': 'action'})
        elif data['info'] == 'result':
            print('win money: {},\tyour card: {},\topp card: {},\t\tpublic card: {}'.format(
                data['players'][position]['win_money'], data['player_card'][position], data['player_card'][1 - position], data['public_card'])) 
            sendJson(client, {'info': 'ready', 'status': 'start'})
            game_street = 0
            last_round_raise = 0
        else:
            print(data)
            break
    client.close()
