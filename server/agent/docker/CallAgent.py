import json
import struct
import socket
import argparse


def get_args():
    parser = argparse.ArgumentParser(description="Agent")
    parser.add_argument('--server_ip', default='poker.xuhang.ink')
    parser.add_argument('--server_port', type=int, default='18888')
    parser.add_argument('--room_id', type=int, required=True)
    parser.add_argument('--name', default='CallAgent')
    parser.add_argument('--room_number', type=int, required=True)
    parser.add_argument('--game_number', type=int, required=True)
    parser.add_argument('--bots', type=str, nargs='+', default=[])
    args = parser.parse_args()
    print(args._get_kwargs())
    return args


def get_action(data):
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
    args = get_args()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((args.server_ip, args.server_port))
    message = dict(info='connect', room_id=args.room_id, name=args.name, room_number=args.room_number, bots=args.bots, game_number=args.game_number)
    sendJson(client, message)
    while True:
        data = recvJson(client)
        if data['info'] == 'state' and data['position'] == data['action_position']:
            action = get_action(data)
            sendJson(client, {'action': action, 'info': 'action'})
        if data['info'] == 'result':
            sendJson(client, {'info': 'ready', 'status': 'start'})
    client.close()
