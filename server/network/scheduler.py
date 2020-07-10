import pika
import json
from config import cfg
import socket
from utils import sendJson
from operator import itemgetter
from err import RoomFullError, MyError, RoomNotExitError, AgentNotFoundError, NoEnoughResource
from logs import logger
from database.rabbitmq import Rabbitmq
from database.mysql import Mysql
from utils import myip, catch_exception
from collections import defaultdict

class Scheduler():

    @catch_exception
    def __init__(self):
        self.rb = Rabbitmq()
        self.mysql = Mysql()
        self.rooms = {}
        # recv connect msg from user
        self.rb.recv_msg_from_queue('connect_queue', self.connect_callback)
        # recv logs
        queue_name = "{}_scheduler_logs".format(myip)
        self.rb.recv_msg_from_direct_exchange(queue_name, 'logs', 'room', self.room_logs_callback)
        # send task
        self.rb.queue_declare('task_queue')
        # send logs
        self.rb.exchange_declare('logs', 'direct')
        # recv agent create error 
        self.rb.recv_msg_from_queue("agent_error_queue", self.agent_error_callback)

    @catch_exception
    def connect_callback(self, ch, method, props, body):
        try:
            data = json.loads(body)
            info = data["info"]
            if info == "connect":
                self.handle_player(data)
            elif info == "ai_vs_ai":
                self.handle_ai_vs_ai(data)
            elif info == "observer":
                self.handle_observer(data)
        except MyError as e:
            self.send_logs(e.text)

    def handle_player(self, data):
        room_id, name, room_number, bots, game_number, uuid = itemgetter('room_id', 'name', 'room_number', 'bots', 'game_number', 'uuid')(data)
        room = self.get_or_create_room(room_id, room_number, game_number)
        self.add_client(room, room_id, name, uuid)
        self.notify_bots(room, bots, data)
        self.check_start(room)

    def handle_ai_vs_ai(self, data):
        room_id, room_number, bots, game_number, uuid = itemgetter('room_id', 'room_number', 'bots', 'game_number', 'uuid')(data)
        room = self.get_or_create_room(room_id, room_number, game_number)
        if len(room['name']) == room['room_number']:
            raise RoomFullError(room_id, uuid)
        self.notify_bots(room, bots, data)

    def handle_observer(self, data):
        room_id = data["room_id"]
        if room_id not in self.rooms:
            raise RoomNotExitError(room_id)

    def get_or_create_room(self, room_id, room_number, game_number):
        if room_id not in self.rooms:
            room = {}
            room['room_id'] = room_id
            room['room_number'] = room_number
            room['game_number'] = game_number
            room['uuid'] = []
            room['name'] = []
            room['notify_bot'] = False
            self.rooms[room_id] = room
        return self.rooms[room_id]

    def add_client(self, room, room_id, name, uuid):
        if len(room['name']) == room['room_number']:
            raise RoomFullError(room_id, uuid)
        room['name'].append(name)
        room['uuid'].append(uuid)

    def notify_bots(self, room, bots, data):
        if room['notify_bot']:
            return
        count = defaultdict(int)
        for bot in bots:
            supported_agent = self.mysql.get_agent()
            if bot not in supported_agent:
                self.send_logs(AgentNotFoundError(data["room_id"], bot).text)
                return
        for bot in bots:
            count[bot] += 1
            suffix = "" if count[bot] == 1 else "_" + str(count[bot]) 
            info = dict(
                room_id=data["room_id"],
                room_number=data["room_number"],
                game_number=data["game_number"],
                bot_name=bot,
                bot_name_suffix=suffix,
                uuid=data["uuid"],
                server=cfg["ext_server"]["host"],
                port=cfg["ext_server"]["port"],
                no_gpu=0
            )
            self.rb.send_msg_to_queue(bot, json.dumps(info))
        room['notify_bot'] = True

    def check_start(self, room):
        if len(room['name']) == room['room_number']:
            self.rb.send_msg_to_queue('task_queue', json.dumps(room))

    @catch_exception
    def room_logs_callback(self, ch, method, props, body):
        data = json.loads(body)
        room_id = data.pop('room_id')
        if room_id in self.rooms:
            del self.rooms[room_id]

    def send_logs(self, message):
        self.rb.send_msg_to_exchange('logs', message['op_type'], json.dumps(message))

    @catch_exception
    def agent_error_callback(self, ch, method, props, body):
        data = json.loads(body)
        room_id = data["room_id"]
        bot_name = data["bot_name"]
        if data["error"] == "no_gpu":
            self.send_logs(NoEnoughResource(room_id, bot_name).text)

    
    def start(self):
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.rb.start()
