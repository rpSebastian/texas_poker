import pika
import uuid
import json
from twisted.internet import protocol
from network.base import JsonReceiver
from logs import logger
from config import cfg
from err import MyError, RoomNotExitError, DisconnectError
from twisted.internet import reactor
from database.redis import Redis
from database.rabbitmq import Rabbitmq
from utils import myip, catch_exception


class GameProtocol(JsonReceiver):

    @catch_exception
    def __init__(self, factory):
        self.factory = factory
        self.game = None
        self.identity = None
        self.room_id = None
        self.uuid = str(uuid.uuid4())

    @catch_exception
    def jsonReceived(self, data):
        if 'room_id' in data:
            data['room_id'] = int(data['room_id'])
        info = data['info']
        peer = self.transport.getPeer()
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
                room['observer'] = {}
                self.factory.rooms[room_id] = room
            room = self.factory.rooms[room_id]
            if info == 'connect':
                self.identity = 'player'
                room['player'][self.uuid] = self
            if info == "observer":
                self.identity = 'observer'
                room['observer'][self.uuid] = self
            if info == 'ai_vs_ai':
                self.identity = 'ai_vs_ai'
                room['observer'][self.uuid] = self
        else:
            self.factory.send_user_message(data, room_id=self.room_id, uuid=self.uuid)

    @catch_exception
    def connectionLost(self, reason):
        # 服务器主动断开客户连接也会触发该程序。主要包括局数打完，某用户发送exit，房间已满，消息格式错误等。
        # 如果断开连接的客户不在房间登记列表中，不进行处理。即只处理客户主动断开的情况。
        if self.room_id not in self.factory.rooms:
            return
        room = self.factory.rooms[self.room_id]
        if self.identity == 'player' and self.uuid in room['player']:
            # 如果是玩家主动断开连接，则该房间无法继续进行游戏，断开所有连接。
            self.factory.send_logs(DisconnectError(self.room_id).text)
        if self.identity == 'observer' and self.uuid in room['observer']:
            # 如果是观察者主动断开连接，直接删除记录，停止之后的消息发送
            del room['observer'][self.uuid]
        if self.identity == 'ai_vs_ai':
            # 如果是ai对战发起者主动断开连接，删除记录，停止之后的消息发送,并且终止房间游戏.
            del room['observer'][self.uuid]
            self.factory.send_logs(DisconnectError(self.room_id).text)


class GameFactory(protocol.Factory):

    @catch_exception
    def __init__(self):
        self.redis = Redis()
        self.rb = Rabbitmq()
        self.rb.queue_declare('connect_queue')
        self.rb.exchange_declare('user_message', 'fanout')
        self.rb.exchange_declare('logs', 'direct')
        self.rooms = {}

    def buildProtocol(self, addr):
        return GameProtocol(self)

    def send_connect_message(self, data):
        self.rb.send_msg_to_queue('connect_queue', json.dumps(data))

    def send_user_message(self, data, room_id, uuid):
        rid = self.redis.save_message(data)
        data = dict(rid=rid, room_id=room_id, uuid=uuid)
        self.rb.send_msg_to_exchange('user_message', '', json.dumps(data))

    def send_logs(self, message):
        self.rb.send_msg_to_exchange('logs', message['op_type'], json.dumps(message))

    @catch_exception
    def start(self):
        rb = Rabbitmq()
        # receive server message
        queue_name = "{}_protocols_server".format(myip)
        rb.recv_msg_from_fanout_exchange(queue_name, 'server_message', self.server_message_callback)
        # receive room logs message
        queue_name = "{}_protocols_room_logs".format(myip)
        rb.recv_msg_from_direct_exchange(queue_name, 'logs', 'room', self.room_logs_callback)
        # receive player logs message
        queue_name = "{}_protocols_player_logs".format(myip)
        rb.recv_msg_from_direct_exchange(queue_name, 'logs', 'player', self.player_logs_callback)

        rb.start()

    @catch_exception
    def server_message_callback(self, ch, method, props, body):
        message = json.loads(body)
        receiver, room_id = message['receiver'], message['room_id']
        # 如果服务器发送消息回来时，用户已经断开了连接，那么此时房间号不存在
        if room_id not in self.rooms:
            return
        room = self.rooms[room_id]
        if receiver == 'player':
            uuid = message['uuid']
            if uuid in room['player']:
                protocol = room['player'][uuid]
                data = self.redis.load_message(message["rid"])
                reactor.callFromThread(self.send_message, protocol, data)
        elif receiver == 'observer':
            data = self.redis.load_message(message["rid"])
            for protocol in room['observer'].values():
                reactor.callFromThread(self.send_message, protocol, data)

    @catch_exception
    def room_logs_callback(self, ch, method, props, body):
        data = json.loads(body)
        room_id = data.pop('room_id')
        del data['op_type']
        if room_id in self.rooms:
            clients = [*self.rooms[room_id]['player'].values(), *self.rooms[room_id]['observer'].values()]
            del self.rooms[room_id]
            for client in clients:
                reactor.callFromThread(self.send_message, client, data)
                reactor.callFromThread(self.lose_connection, client)

    @catch_exception
    def player_logs_callback(self, ch, method, props, body):
        data = json.loads(body)
        room_id = data.pop('room_id')
        uuid = data.pop('uuid')
        del data['op_type']
        if room_id in self.rooms and uuid in self.rooms[room_id]['player']:
            client = self.rooms[room_id]['player'].pop(uuid)
            reactor.callFromThread(self.send_message, client, data)
            reactor.callFromThread(self.lose_connection, client)
        if room_id in self.rooms and uuid in self.rooms[room_id]['observer']:
            client = self.rooms[room_id]['observer'].pop(uuid)
            reactor.callFromThread(self.send_message, client, data)
            reactor.callFromThread(self.lose_connection, client)

    def send_message(self, protocol, message):
        protocol.sendJson(message)

    def lose_connection(self, protocol):
        protocol.transport.loseConnection()
