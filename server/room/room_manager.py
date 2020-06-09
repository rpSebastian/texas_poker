import json
import pika
from config import cfg
from room import NoLimitHoldemRoom
from database.mysql import Mysql
from operator import itemgetter
from multiprocessing import Process
from database.redis import Redis
from database.rabbitmq import Rabbitmq
from logs import logger
from utils import catch_exception
from utils import myip


class People():
    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid
        self.session = 0
        self.times = 0

    def update_session(self, money):
        self.times += 1
        self.session += money

    def print_session(self):
        print(f'{self.name} : {self.session} after {self.times} matchs, {self.session * 10 / self.times} mbb/g')


class RoomManager(Process):
    
    @catch_exception
    def __init__(self, ps_id):
        super().__init__()
        self.rooms = {}
        self.mysql = Mysql()
        self.redis = Redis()
        self.rb = Rabbitmq()
        # recv msg from schedulre
        self.rb.recv_msg_from_queue('task_queue', self.task_callback)
        # recv msg from user
        queue_name = "{}_room_manger{}_user_message".format(myip, ps_id)
        self.rb.recv_msg_from_fanout_exchange(queue_name, 'user_message', self.action_callback)
        # recv log msg
        queue_name = '{}_room_manger{}_logs'.format(myip, ps_id)
        self.rb.recv_msg_from_direct_exchange(queue_name, 'logs', 'room', self.room_logs_callback)
        # send to user
        self.rb.exchange_declare('server_message', 'fanout')
        # send to logs
        self.rb.exchange_declare('logs', 'direct')

    @catch_exception
    def task_callback(self, ch, method, props, body):
        data = json.loads(body)
        room_id, room_number, game_number, uuids, names = itemgetter('room_id', 'room_number', 'game_number', 'uuid', 'name')(data)
        clients = [People(name, uuid) for uuid, name in zip(uuids, names)]
        self.rooms[room_id] = NoLimitHoldemRoom(self, clients, room_id, room_number, game_number, self.mysql)
        self.rooms[room_id].init_game()

    @catch_exception
    def action_callback(self, ch, method, props, body):
        data = json.loads(body)
        room_id, uuid = itemgetter('room_id', 'uuid')(data)
        if room_id in self.rooms:
            data = self.redis.load_message(data["rid"])
            self.rooms[room_id].handle(uuid, data)

    @catch_exception
    def room_logs_callback(self, ch, method, props, body):
        data = json.loads(body)
        room_id = data.pop('room_id')
        if room_id in self.rooms:
            del self.rooms[room_id]

    def send_message(self, state, room_id, receiver, uuid=None):
        rid = self.redis.save_message(state)
        message = dict(rid=rid, room_id=room_id, receiver=receiver)
        if uuid is not None:
            message["uuid"] = uuid
        logger.info(message)
        self.rb.send_msg_to_exchange('server_message', '', json.dumps(message))

    def send_logs(self, message):
        self.rb.send_msg_to_exchange('logs', message['op_type'], json.dumps(message))

    def run(self):
        self.rb.start()
