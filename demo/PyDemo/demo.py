import json
import struct 
import socket

server_ip = "poker.xuhang.ink"    # 德州扑克平台地址
server_port = 18888               # 德州扑克平台开放端口
room_id = 120                     # 进行对战的房间号
name = "test"                     # 当前程序的 AI 名字
room_number = 2                   # 德州扑克游戏人数
bots = ["CallAgent"]              # 需要平台添加的AI数量，目前支持 "CallAgent", "AllinAgent", "RandomAgent", "RuleAgnet"

def get_action(data):
    """ 根据游戏的状态信息，返回对应的动作。
    
    Args:
        data: dict 表示游戏的状态
    
    Return:
        action: string 表示制定的动作
    """
    if 'call' in data['legal_actions']:
        action = 'call'
    else:
        action = 'check'
    return action 

def sendJson(request, jsonData):
    """ 向套接字发送json数据。 首先发送长度为4的数据长度，再发送数据。
    """
    data = json.dumps(jsonData).encode()
    request.send(struct.pack('i', len(data)))
    request.sendall(data)
  
def recvJson(request):
    """ 从套接字中接受json数据，首先接收长度为4的数据长度，再接收数据。
    """
    l = struct.unpack('i', request.recv(4))[0]
    data = json.loads(request.recv(l).decode())
    return data
  
if __name__ == "__main__":
    # 初始化套接字
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    client.connect((server_ip, server_port)) 
    # 发送创建连接消息
    message = dict(info='connect', room_id=room_id, name=name, room_number=2, bots=bots)
    sendJson(client, message)   
    # 接收对战玩家消息
    data = recvJson(client)
    # 发送游戏开始消息
    sendJson(client, {'info': 'start'})
    while True:
        data = recvJson(client)
        # 接收游戏状态消息
        if data['info'] == 'state' and data['position'] == data['action_position']:
            position = data['position']
            action = get_action(data)
            # 发送执行动作消息
            sendJson(client, {'action': action, 'info': 'action'})
        # 接收游戏结果消息
        if data['info'] == 'result':
            print('win money: {},\tyour card: {},\topp card: {},\t\tpublic card: {}'.format(data['win_money'][position], data['player_card'][position],  data['player_card'][1-position], data['public_card']))
            # 发送游戏开始消息
            sendJson(client, {'info': 'start'})
    client.close()