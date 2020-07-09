import json
import random
import struct
import socket
import multiprocessing

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

class CallAgent(multiprocessing.Process):

    def __init__(self, room_id, room_number, name, game_number, server, port):
        multiprocessing.Process.__init__(self)
        self.info = dict(info='connect', room_id=room_id, name=name, room_number=room_number, game_number=game_number, bots=[])
        self.server = server
        self.port = port

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server, self.port))
        try:
            sendJson(client, self.info)
            while True:
                data = recvJson(client)
                if data['info'] == 'state' and data['position'] == data['action_position']:
                    if 'call' in data['legal_actions']:
                        action = 'call'
                    else:
                        action = 'check'
                    sendJson(client, {'action': action, 'info': 'action'})
                if data['info'] == 'result':
                    sendJson(client, {'info': 'ready', 'status': 'start'})
        except Exception as e:
            pass
        finally:
            client.close()


class RandomAgent(multiprocessing.Process):

    def __init__(self, room_id, room_number, name, game_number, server, port):
        multiprocessing.Process.__init__(self)
        self.info = dict(info='connect', room_id=room_id, name=name, room_number=room_number, game_number=game_number, bots=[])
        self.server = server
        self.port = port

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server, self.port))
        try:
            sendJson(client, self.info)
            while True:
                data = recvJson(client)
                if data['info'] == 'state' and data['position'] == data['action_position']:
                    if 'fold' in data['legal_actions']:
                        data['legal_actions'].remove('fold')
                    choose_index = random.randint(0, len(data['legal_actions']) - 1)
                    if data['legal_actions'][choose_index] == 'raise':
                        action = 'r' + str(random.randint(data['raise_range'][0], data['raise_range'][1]))
                    else:
                        action = data['legal_actions'][choose_index]
                    sendJson(client, {'action': action, 'info': 'action'})
                if data['info'] == 'result':
                    sendJson(client, {'info': 'ready', 'status': 'start'})
        except Exception as e:
            pass
        finally:
            client.close()


class AllinAgent(multiprocessing.Process):

    def __init__(self, room_id, room_number, name, game_number, server, port):
        multiprocessing.Process.__init__(self)
        self.info = dict(info='connect', room_id=room_id, name=name, room_number=room_number, game_number=game_number, bots=[])
        self.server = server
        self.port = port

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server, self.port))
        try:
            sendJson(client, self.info)
            while True:
                data = recvJson(client)
                if data['info'] == 'state' and data['position'] == data['action_position']:
                    action = 'r' + str(data['raise_range'][1])
                    sendJson(client, {'action': action, 'info': 'action'})
                if data['info'] == 'result':
                    sendJson(client, {'info': 'ready', 'status': 'start'})
        except Exception:
            pass
        finally:
            client.close()