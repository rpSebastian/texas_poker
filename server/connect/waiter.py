import yaml
import socket
import multiprocessing
import collections
from .splayer import SPlayer
from kernel.nolimitholdemkernel import NoLimitHoldemKernel
from kernel.slumbotkernel import SlumbotKernel
from eval.lbr import LocalBestResbonse
from utils.utils import sendJson, recvJson
from logs import logger
from operator import itemgetter

with open("./config/config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)


class Waiter(multiprocessing.Process):
    def __init__(self, waiting_queue):
        multiprocessing.Process.__init__(self)
        self.waiting_list = collections.defaultdict(list)
        self.notify_bot_done = collections.defaultdict(bool)
        self.q = waiting_queue
        self.room_queues = {}

    def run(self):
        while True:
            try:
                self.process()
            except Exception as e:
                logger.exception(e)

    def process(self):
        client, addr = self.q.get()
        message = recvJson(client)
        logger.info("recv client from {} : {}", addr, message)
        info = message["info"]
        if info == 'lbr':
            self.handle_lbr(client, message)
        elif info == 'observer':
            self.handle_observer(client, message)
        elif info == "connect":
            self.handle_player(client, message)
        elif info == "ai_vs_ai":
            self.handle_ai_vs_ai(client, message)

    def handle_ai_vs_ai(self, client, message):
        room_id, room_number, bots = itemgetter('room_id', 'room_number', 'bots')(message)
        self.notify_bot_done[room_id] = True
        self.notify_bot(room_id, room_number, bots)
        if room_id not in self.room_queues:
            self.room_queues[room_id] = multiprocessing.Queue()
        self.room_queues[room_id].put(client)

    def handle_lbr(self, client, message):
        name, method = itemgetter('name', 'method')(message)
        LocalBestResbonse(SPlayer(client, name), method).start()

    def handle_observer(self, client, message):
        room_id = message['room_id']
        self.room_queues[room_id].put(client)

    def handle_player(self, client, message):
        room_id, name, room_number, bots = itemgetter('room_id', 'name', 'room_number', 'bots')(message)
        if room_number == 2 and len(bots) == 1 and bots[0] == 'slumbot':
            self.room_queues[room_id] = multiprocessing.Queue()
            SlumbotKernel(name, client, self.room_queues[room_id]).start()
            return
        if "LuaStack" in bots and room_number != 2:
            return
        if not self.notify_bot_done[room_id]:
            self.notify_bot(room_id, room_number, bots)
            self.notify_bot_done[room_id] = True
        self.waiting_list[room_id].append(SPlayer(client, name))
        if len(self.waiting_list[room_id]) == int(room_number):
            if room_id not in self.room_queues:
                self.room_queues[room_id] = multiprocessing.Queue()
            NoLimitHoldemKernel(self.waiting_list[room_id], self.room_queues[room_id]).start()
            self.waiting_list[room_id] = []
            self.notify_bot_done[room_id] = False

    def notify_bot(self, room_id, room_number, bots):
        num = 0
        for bot in bots:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if bot not in cfg["bot"]:
                bot = "CallAgent"
            client.connect((cfg["bot"][bot]["host"], cfg["bot"][bot]["port"]))
            sendJson(client, [room_id, room_number, bot+str(num)])
            client.close()
            num += 1
