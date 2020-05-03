import pika
import uuid
import json
from twisted.internet import protocol
from network.base import JsonReceiver
from logs import logger
from config import cfg
from err import MyError, RoomNotExitError, DisconnectError


class GameProtocol(JsonReceiver):

    def __init__(self, factory):
        self.factory = factory
        self.game = None
        self.room = None
        self.identity = None
        self.room_id = None
        self.uuid = str(uuid.uuid4())

    def jsonReceived(self, data):
        try:
            info = data['info']
            peer = self.transport.getPeer()
            # logger.info("recv client from {}, {}: {}", peer.host, peer.port, info)
            if info == 'connect' or info == 'observer' or info == 'ai_vs_ai':
                logger.info("recv client from {}, {}: {}", peer.host, peer.port, data)
                data['uuid'] = self.uuid
                # send connect message to scheduler
                self.factory.send_connect_message(data)
                # record room and player infomation
                room_id = data['room_id']
                self.room_id = room_id
                if room_id not in self.factory.rooms:
                    room = {}
                    room['player'] = {}
                    room['observer'] = []
                    self.factory.rooms[room_id] = room
                room = self.factory.rooms[room_id]
                if info == 'connect':
                    self.identity = 'player'
                    room['player'][self.uuid] = self
                if info == "observer" or info == 'ai_vs_ai':
                    self.identity = 'observer'
                    room['observer'].append(self)
            else:
                data['uuid'] = self.uuid
                data['room_id'] = self.room_id
                self.factory.send_user_message(data)
        except Exception as e:
            logger.exception(e)

    def connectionLost(self, reason):
        # 服务器主动断开客户连接也会触发该程序。主要包括局数打完，某用户发送exit，房间已满，消息格式错误等。
        # 如果断开连接的客户不在房间登记列表中，不进行处理。即只处理客户主动断开的情况。
        if self.room_id not in self.factory.rooms:
            return
        room = self.factory.rooms[self.room_id]
        if self.identity == 'player' and self.uuid in room['player']:
            # 如果是玩家主动断开连接，则该房间无法继续进行游戏，断开所有连接。
            self.factory.send_logs(DisconnectError(self.room_id).text)
        if self.identity == 'observer' and self in room['observer']:
            # 如果是观察者主动断开连接，直接删除记录，停止之后的消息发送
            room['observer'].remove(self)


class GameFactory(protocol.Factory):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=cfg["rabbitMQ"]["host"]))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='connect_queue')
        self.channel.exchange_declare(exchange='user_message', exchange_type='fanout')
        # send logs through logs exchange
        self.channel.exchange_declare(exchange='logs', exchange_type='direct')
        self.rooms = {}

    def buildProtocol(self, addr):
        return GameProtocol(self)

    def send_connect_message(self, data):
        self.channel.basic_publish(exchange='', routing_key='connect_queue', body=json.dumps(data))

    def send_user_message(self, data):
        self.channel.basic_publish(exchange='user_message', routing_key='', body=json.dumps(data))

    def send_logs(self, message):
        self.channel.basic_publish(exchange='logs', routing_key=message['op_type'], body=json.dumps(message))

    def start(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=cfg["rabbitMQ"]["host"]))
        channel = connection.channel()
        # receive server message 
        channel.exchange_declare(exchange='server_message', exchange_type='fanout')
        queue_name = channel.queue_declare(queue='').method.queue
        channel.queue_bind(exchange='server_message', queue=queue_name)
        channel.basic_consume(queue=queue_name, on_message_callback=self.server_message_callback, auto_ack=True)
        # receive room logs message
        channel.exchange_declare(exchange='logs', exchange_type='direct')
        queue_name = channel.queue_declare(queue='').method.queue
        channel.queue_bind(exchange='logs', queue=queue_name, routing_key='room')
        channel.basic_consume(queue=queue_name, on_message_callback=self.room_logs_callback, auto_ack=True)
        # receive player logs message
        channel.exchange_declare(exchange='logs', exchange_type='direct')
        queue_name = channel.queue_declare(queue='').method.queue
        channel.queue_bind(exchange='logs', queue=queue_name, routing_key='player')
        channel.basic_consume(queue=queue_name, on_message_callback=self.player_logs_callback, auto_ack=True)
        
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()

    def server_message_callback(self, ch, method, props, body):
        data = json.loads(body)
        receiver, room_id = data.pop('receiver'), data.pop('room_id')
        # 如果服务器发送消息回来时，用户已经断开了连接，那么此时房间号不存在
        if room_id not in self.rooms:
            return
        room = self.rooms[room_id]
        if receiver == 'player':
            uuid = data.pop('uuid')
            if uuid in room['player']:
                protocol = room['player'][uuid]
                protocol.sendJson(data)
        elif receiver == 'observer':
            for protocol in room['observer']:
                protocol.sendJson(data)

    def room_logs_callback(self, ch, method, props, body):
        data = json.loads(body)
        room_id = data.pop('room_id')
        del data['op_type']
        if room_id in self.rooms:
            clients = [*self.rooms[room_id]['player'].values(), *self.rooms[room_id]['observer']]
            del self.rooms[room_id]
            for client in clients:
                client.sendJson(data)
                client.transport.loseConnection()

    def player_logs_callback(self, ch, method, props, body):
        data = json.loads(body)
        room_id = data.pop('room_id')
        uuid = data.pop('uuid')
        del data['op_type']
        if room_id in self.rooms and uuid in self.rooms[room_id]['player']:
            client = self.rooms[room_id]['player'].pop(uuid)
            client.sendJson(data)
            client.transport.loseConnection()
