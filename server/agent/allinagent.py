import yaml
import socket
from utils.utils import sendJson, recvJson
import multiprocessing
import random
with open("./config/config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)


class AllinAgentListener(multiprocessing.Process):

    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((cfg["bot"]["AllinAgent"]["host"], cfg["bot"]["AllinAgent"]["port"]))
        server.listen(20)
        while True:
            client, addr = server.accept()
            room_id, room_number, name, game_number = recvJson(client)
            client.close()
            agent = AllinAgent(room_id, room_number, name, game_number)
            agent.start()


class AllinAgent(multiprocessing.Process):

    def __init__(self, room_id, room_number, name, game_number):
        multiprocessing.Process.__init__(self)
        self.info = dict(info='connect', room_id=room_id, name=name, room_number=room_number, game_number=game_number, bots=[])
        self.seed = random.randint(0, 30)

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((cfg["server"]["host"], cfg["server"]["port"]))
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
