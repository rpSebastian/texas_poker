import yaml
import socket
from utils.utils import sendJson, recvJson
import multiprocessing
import random

with open("./config/config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)


class RandomAgentListener(multiprocessing.Process):

    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((cfg["bot"]["RandomAgent"]["host"], cfg["bot"]["RandomAgent"]["port"]))
        server.listen(20)
        while True:
            client, addr = server.accept()
            room_id, room_number, name = recvJson(client)
            client.close()
            agent = RandomAgent(room_id, room_number, name)
            agent.start()


class RandomAgent(multiprocessing.Process):

    def __init__(self, room_id, room_number, name):
        multiprocessing.Process.__init__(self)
        self.info = dict(info='connect', room_id=room_id, name="RanAgent" + name[-1], room_number=room_number, bots=[])
        self.seed = random.randint(0, 30)

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((cfg["server"]["host"], cfg["server"]["port"]))
        try:
            sendJson(client, self.info)
            data = recvJson(client)
            sendJson(client, {'info': 'start'})
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
                    sendJson(client, {'info': 'start'})
        except Exception:
            pass
        finally:
            client.close()
