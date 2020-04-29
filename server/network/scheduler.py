import pika
import json
from config import config
import collections

class Scheduler():
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=config["rabbitMQ"]["host"]))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='connect_queue')
        self.channel.basic_consume(queue='connect_queue', on_message_callback=self.callback)
        self.rooms = 

    def callback(self, ch, method, props, body):
        data = json.loads(body)
        info = data["info"]
        if info == "connect":
            self.handle_player(data)
        elif info == "ai_vs_ai":
            self.handle_ai_vs_ai(data)

    def handle_player(self, data):
        self.identity = 'player'
        room_id, name, room_number, bots, game_number = itemgetter('room_id', 'name', 'room_number', 'bots', 'game_number')(data)
        self.room_id = room_id
        self.factory.room_manager.create_room(room_id, room_number, game_number)
        self.factory.room_manager.add_client(room_id, self, name)
        self.factory.room_manager.notify_bots(room_id, bots)
        self.factory.room_manager.check_start(room_id)

    def handle_ai_vs_ai(self, data):
        room_id, room_number, bots, game_number = itemgetter('room_id', 'room_number', 'bots', 'game_number')(data)
        self.factory.room_manager.create_room(room_id, room_number, game_number)
        self.factory.room_manager.notify_bots(room_id, bots)
        self.handle_observer(data)

    def start(self):
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

Scheduler().start()
