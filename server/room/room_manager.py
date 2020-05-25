import json
import pika
from config import cfg
from room import NoLimitHoldemRoom
from database.mysql import Mysql
from operator import itemgetter
from multiprocessing import Process

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
    def __init__(self):
        super().__init__()
        self.rooms = {}
        self.mysql = Mysql()
        credentials= pika.PlainCredentials(cfg["rabbitMQ"]["username"], cfg["rabbitMQ"]["password"])
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=cfg["rabbitMQ"]["host"],credentials=credentials, heartbeat=0))
        self.channel = self.connection.channel()
        # receive room info from task_queue
        self.channel.queue_declare(queue='task_queue')
        self.channel.basic_consume(queue='task_queue', on_message_callback=self.task_callback, auto_ack=True)
        # send state message through server_message exchange
        self.channel.exchange_declare(exchange='server_message', exchange_type='fanout')
        # receive action message throung queue_name binding user_message exchange
        self.channel.exchange_declare(exchange='user_message', exchange_type='fanout')
        queue_name = self.channel.queue_declare(queue='').method.queue
        self.channel.queue_bind(exchange='user_message', queue=queue_name)
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.action_callback, auto_ack=True)
        # send logs through logs exchange
        self.channel.exchange_declare(exchange='logs', exchange_type='direct')
        # receive room logs message
        self.channel.exchange_declare(exchange='logs', exchange_type='direct')
        queue_name = self.channel.queue_declare(queue='').method.queue
        self.channel.queue_bind(exchange='logs', queue=queue_name, routing_key='room')
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.room_logs_callback, auto_ack=True)

    def room_logs_callback(self, ch, method, props, body):
        data = json.loads(body)
        room_id = data.pop('room_id')
        if room_id in self.rooms:
            del self.rooms[room_id]

    def task_callback(self, ch, method, props, body):
        data = json.loads(body)
        room_id, room_number, game_number, uuids, names = itemgetter('room_id', 'room_number', 'game_number', 'uuid', 'name')(data)
        clients = []
        for uuid, name in zip(uuids, names):
            clients.append(People(name, uuid))
        self.rooms[room_id] = NoLimitHoldemRoom(self, clients, room_id, room_number, game_number, self.mysql)
        self.rooms[room_id].init_game()

    def action_callback(self, ch, method, props, body):
        data = json.loads(body)
        room_id, uuid = itemgetter('room_id', 'uuid')(data)
        if room_id in self.rooms:
            self.rooms[room_id].handle(uuid, data)

    def create_room(self, room_id, room_number, game_number):
        if room_id not in self.rooms:
            self.rooms[room_id] = NoLimitHoldemRoom(room_number, room_id, game_number, self.mysql)

    def send_message(self, message):
        self.channel.basic_publish(exchange='server_message', routing_key='', body=json.dumps(message))

    def send_logs(self, message):
        self.channel.basic_publish(exchange='logs', routing_key=message['op_type'], body=json.dumps(message))

    def run(self):
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()
