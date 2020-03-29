import yaml
import socket
from utils.utils import sendJson, recvJson
import multiprocessing
import random

with open("./config/config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)


class CallAgentListener(multiprocessing.Process):

    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((cfg["bot"]["CallAgent"]["host"], cfg["bot"]["CallAgent"]["port"]))
        server.listen(20)
        while True:
            client, addr = server.accept()
            room_id, room_number, name = recvJson(client)
            client.close()
            agent = CallAgent(room_id, room_number, name)
            agent.start()


class CallAgent(multiprocessing.Process):

    def __init__(self, room_id, room_number, name):
        multiprocessing.Process.__init__(self)
        self.info = dict(info='connect', room_id=room_id, name=name, room_number=room_number, bots=[])
        self.seed = random.randint(0, 30)

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((cfg["server"]["host"], cfg["server"]["port"]))
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
        except Exception:
            pass
        finally:
            client.close()
