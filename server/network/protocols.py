import pika
import uuid
import json
from twisted.internet import protocol
from network.base import JsonReceiver
from operator import itemgetter
from room import RoomManager
from logs import logger
from config import config


class GameProtocol(JsonReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.game = None
        self.room = None
        self.identity = None
        self.room_id = None
        self.uuid = uuid.uuid4()

    def jsonReceived(self, data):
        try:
            info = data["info"]
            peer = self.transport.getPeer()
            logger.info("recv client from {}, {}: {}", peer.host, peer.port, data)
            data["uuid"] = self.uuid
            if info == "connect" or info == "observer" or info == "ai_vs_ai":
                self.factory.send_connect_message(data)
            else:
                self.factory.send_user_message(data)
        except Exception as e:
            logger.exception(e)
            self.transport.loseConnection()

    def connectionLost(self, reason):
        if self.room_id is not None:
            self.factory.room_manager.handle_lost(self.room_id, self)


class GameFactory(protocol.Factory):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=config["rabbitMQ"]["host"]))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='connect_queue')
        self.channel.exchange_declare(exchange='user_message', exchange_type='fanout')
        self.channel.exchange_declare(exchange='server_message', exchange_type='fanout')
        queue_name = self.channel.queue_declare(queue='', exclusive=True).method.name
        self.channel.queue_bind(exchange='server_message', queue=queue_name)

    def buildProtocol(self, addr):
        return GameProtocol(self)

    def send_connect_message(self, data):
        self.channel.basic_publish(exchange='', routing_key='connect_queue', body=json.dumps(data))

    def send_user_message(self, data):
        self.channel.basic_publish(exchange='server_message', routing_key='', body=json.dumps(data))
