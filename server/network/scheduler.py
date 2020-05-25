import pika
import json
from config import cfg
import socket
from utils import sendJson
from operator import itemgetter
from err import RoomFullError, MyError, RoomNotExitError
from logs import logger


class Scheduler():
    def __init__(self):
        credentials= pika.PlainCredentials(cfg["rabbitMQ"]["username"], cfg["rabbitMQ"]["password"])
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=cfg["rabbitMQ"]["host"],credentials=credentials, heartbeat=0))
        self.channel = self.connection.channel()
        # receive connect message through connect_queue
        self.channel.queue_declare(queue='connect_queue')
        self.channel.basic_consume(queue='connect_queue', on_message_callback=self.callback, auto_ack=True)
        # send task through task queue
        self.channel.queue_declare(queue='task_queue')
        # send logs through logs exchange
        self.channel.exchange_declare(exchange='logs', exchange_type='direct')
        # receive room logs message
        self.channel.exchange_declare(exchange='logs', exchange_type='direct')
        queue_name = self.channel.queue_declare(queue='').method.queue
        self.channel.queue_bind(exchange='logs', queue=queue_name, routing_key='room')
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.room_logs_callback, auto_ack=True)
        self.rooms = {}

    def room_logs_callback(self, ch, method, props, body):
        data = json.loads(body)
        room_id = data.pop('room_id')
        if room_id in self.rooms:
            del self.rooms[room_id]

    def callback(self, ch, method, props, body):
        try:
            data = json.loads(body)
            logger.info('recv connect message {}', data)
            info = data["info"]
            if info == "connect":
                self.handle_player(data)
            elif info == "ai_vs_ai":
                self.handle_ai_vs_ai(data)
            elif info == "observer":
                self.handle_observer(data)
        except MyError as e:
            self.send_logs(e.text)
        except Exception as e:
            logger.exception(e)

    def handle_player(self, data):
        self.identity = 'player'
        room_id, name, room_number, bots, game_number, uuid = itemgetter('room_id', 'name', 'room_number', 'bots', 'game_number', 'uuid')(data)
        room = self.get_or_create_room(room_id, room_number, game_number)
        self.add_client(room, room_id, name, uuid)
        self.notify_bots(room, bots)
        self.check_start(room)

    def handle_ai_vs_ai(self, data):
        room_id, room_number, bots, game_number, uuid = itemgetter('room_id', 'room_number', 'bots', 'game_number', 'uuid')(data)
        room = self.get_or_create_room(room_id, room_number, game_number)
        if len(room['name']) == room['room_number']:
            raise RoomFullError(room_id, uuid)
        self.notify_bots(room, bots)

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

    def notify_bots(self, room, bots):
        if room['notify_bot']:
            return
        num = ''
        for bot in bots:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if bot not in cfg["bot"]:
                bot = "CallAgent"
            client.connect((cfg["bot"][bot]["host"], cfg["bot"][bot]["port"]))
            sendJson(client, [room['room_id'], room['room_number'], bot+str(num), room['game_number']])
            client.close()
            num = 2 if num == '' else num + 1
        room['notify_bot'] = True

    def check_start(self, room):
        if len(room['name']) == room['room_number']:
            self.channel.basic_publish(exchange='', routing_key='task_queue', body=json.dumps(room))

    def start(self):
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def send_logs(self, message):
        self.channel.basic_publish(exchange='logs', routing_key=message['op_type'], body=json.dumps(message))
