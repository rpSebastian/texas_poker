import copy
import time
import json
import socket
import random
from collections import defaultdict
import multiprocessing
from multiprocessing import reduction
from operator import itemgetter

import gevent
import gevent.monkey
gevent.monkey.patch_all()
import gipc

from utils import utils, hint, err
from utils.logs import logger
from utils.config import cfg
from games.nolimitholdem.game import Game as holdem_game
from database import rabbitmq, mysql


class Player():
    def __init__(self, sock, name=None):
        self.name = name
        self.sock = sock
        self.session = 0
        self.times = 0

    def update_session(self, money):
        self.times += 1
        self.session += money

    def print_session(self):
        print(f'{self.name} : {self.session} after {self.times} matchs, {self.session * 10 / self.times} mbb/g')

    def notify(self, data):
        utils.sendJson(self.sock, data)

    def recv(self):
        data = utils.recvJson(self.sock)
        return data
    
    def finish(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        self.sock.close()


class Game():
    def __init__(self, room_id, room_number, game_number, names, socks, rb, observer_queue, is_ai):
        self.room_id = room_id
        self.room_number = room_number
        self.game_number = game_number
        self.players = []
        self.observers = []
        for name, sock in zip(names, socks):
            self.players.append(Player(sock, name))
        self.rb = rb
        self.observer_queue = observer_queue
        self.is_ai = is_ai

    def retrive_observer(self):
        while self.observer_queue[self.room_id]:
            sock = self.observer_queue[self.room_id].pop(0)
            self.observers.append(Player(sock))

    def run(self):
        try:
            self.work()
        except Exception as e:
            logger.exception(e)
            self.tear_down(hint.unknown_error_info(repr(e)))
    
    def work(self):
        random.shuffle(self.players)
        self.record_game = holdem_game(self.room_number)
        for game_count in range(1, self.game_number + 1):
            if not self.is_ai or self.is_ai and game_count % self.room_number == 1:
                self.record_player = self.record_game.game_init()
            player_id = self.record_player
            self.game =  copy.deepcopy(self.record_game)    
            while not self.game.is_terminal():
                self.retrive_observer()
                self.notify_state()
                
                data = self.players[player_id].recv()
                if data is None:
                    self.tear_down(hint.disconnect_info(self.players[player_id].name))
                    return

                try:
                    player_id = self.game.step(data["action"])
                except err.InvalidActionError as e:
                    self.tear_down(hint.invalid_action_info(self.players[player_id].name, e.action))
                    return

            self.notify_state(last=True)
            self.notify_result()
            self.save_data()
            for player in self.players:
                data = player.recv()
                if data is None:
                    self.tear_down(hint.disconnect_info(player.name))
                    return
                if data["info"] != "ready":
                    self.tear_down(hint.player_exit_info(player.name))
                    return
            player = self.players.pop(0)
            self.players.append(player)

        self.tear_down(hint.play_compelete_info)
    
    def save_data(self):
        message = self.game.get_save_data()
        message['name'] = [p.name for p in self.players]
        message['position'] = [i for i in range(len(self.players))]
        message['room_id'] = self.room_id
        self.rb.send_msg_to_queue("mysql_queue", json.dumps(message))

    def tear_down(self, info=None):
        for player in [*self.players, *self.observers]:
            player.notify(info)
        for player in [*self.players, *self.observers]:
            player.finish()
        if info["info"] != "success":
            logger.warning("room {}, {}", self.room_id, info["text"])
        self.rb.send_msg_to_queue("room_end_queue", json.dumps([self.room_id]))

    def notify_state(self, last=False):
        for i, player in enumerate(self.players):
            state = self.game.get_state(i)
            for j, p in enumerate(self.players):
                state['players'][j]['name'] = p.name
            state['info'] = 'state'
            if last:
                state['action_position'] = -1
            player.notify(state)

        state = self.game.get_public_state()
        if last:
            state['action_position'] = -1
        state['info'] = 'state'
        for j, p in enumerate(self.players):
            state['players'][j]['name'] = p.name
        for observer in self.observers:
            observer.notify(state)
        
    def notify_result(self):
        for i, player in enumerate(self.players):
            state = self.game.get_payoff(i)
            state['info'] = 'result'
            for j, p in enumerate(self.players):
                state['players'][j]['name'] = p.name
            player.notify(state)
            player.update_session(state['players'][i]['win_money'])

        state = self.game.get_payoff()
        state['info'] = 'result'
        state['total_money'] = [p.session for p in self.players]
        state['times'] = [p.times for p in self.players]
        for j, p in enumerate(self.players):
            state['players'][j]['name'] = p.name
        for observer in self.observers:
            observer.notify(state)

def worker(socket_reader, data_reader):
    rb = rabbitmq.Rabbitmq()
    rb.queue_declare("room_end_queue")
    rb.queue_declare("mysql_queue")
    observer_queue = defaultdict(list)
    while True:
        data = data_reader.get()
        if data["info"] == "room":
            room_id, room_number, game_number, names, is_ai = data["data"]
            socks = []
            for i in range(room_number):
                socket_reader.poll(None)
                sock = socket.fromfd(reduction.recv_handle(socket_reader), socket.AF_INET, socket.SOCK_STREAM)
                socks.append(sock)
            game = Game(room_id, room_number, game_number, names, socks, rb, observer_queue, is_ai)
            gevent.spawn(game.run)

        if data["info"] == "observer":
            room_id = data["data"][0]
            socket_reader.poll(None)
            sock = socket.fromfd(reduction.recv_handle(socket_reader), socket.AF_INET, socket.SOCK_STREAM)
            observer_queue[room_id].append(sock)

class WorkerControler():
    def __init__(self):
        self.socket_r, self.socket_w = multiprocessing.Pipe()
        self.data_r, self.data_w = gipc.pipe()
        self.p = gipc.start_process(target=worker, args=(self.socket_r, self.data_r))

    def dispatch(self, room):
        self.data_w.put(dict(info="room", data=[room.room_id, room.room_number, room.game_number, room.names, room.is_ai]))
        for sock in room.socks:
            reduction.send_handle(self.socket_w, sock.fileno(), self.p.pid)

    def dispatch_observer(self, sock, room_id):
        self.data_w.put(dict(info="observer", data=[room_id]))
        reduction.send_handle(self.socket_w, sock.fileno(), self.p.pid)

class Room():
    def __init__(self, room_id, room_number, game_number, bots, control_id, is_ai):
        self.socks = []
        self.names = []
        self.room_number = room_number
        self.game_number = game_number
        self.room_id = room_id
        self.bots = bots
        self.notify_bot_done = False
        self.control_id = control_id
        self.is_ai = is_ai

    def add_player(self, sock, name):
        self.socks.append(sock)
        self.names.append(name)
    
    def full(self):
        return len(self.socks) == self.room_number
    
    def notify_bots(self, supported_agent, rb):
        if self.notify_bot_done:
            return True, None
        self.notify_bot_done = True  
        count = defaultdict(int)
        for bot in self.bots:
            if bot not in supported_agent:
                return False, bot
        for bot in self.bots:
            count[bot] += 1
            suffix = "" if count[bot] == 1 else str(count[bot] - 1) 
            info = dict(
                room_id=self.room_id,
                room_number=self.room_number,
                game_number=self.game_number,
                bot_name=bot,
                bot_name_suffix=suffix,
                server=cfg["ext_server"]["host"],
                port=cfg["ext_server"]["port"],
                no_gpu=0
            )
            rb.send_msg_to_queue(bot, json.dumps(info))
        return True, None

    def dismiss(self, info):
        for sock in self.socks:
            if info is not None:
                utils.sendJson(sock, info)
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            sock.close()

class Listener():
    def __init__(self, address, port, controlers, room_end_queue, agent_error_queue):
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((address, port))
        self.s.listen(100)
        self.controlers = controlers
        self.rooms = {}
        self.cur_control = 0
        self.db = mysql.Mysql()
        self.rb = rabbitmq.Rabbitmq()
        self.room_end_queue = room_end_queue
        self.agent_error_queue = agent_error_queue
        self.supported_agent = self.db.get_agent()
        
    def run(self):
        tasks = [
            gevent.spawn(self.clear_room),
            gevent.spawn(self.recv_user),
            gevent.spawn(self.update_agent_list)
        ]
        gevent.joinall(tasks)

    @utils.run_forever
    @utils.catch_exception
    def update_agent_list(self):
        self.supported_agent = self.db.get_agent()
        gevent.sleep(10)

    @utils.run_forever
    @utils.catch_exception
    def clear_room(self):
        while not self.room_end_queue.empty():
            room_id = self.room_end_queue.get()
            if room_id in self.rooms:
                del self.rooms[room_id]
        
        while not self.agent_error_queue.empty():
            msg = self.agent_error_queue.get()
            room_id = msg["room_id"]
            bot_name = msg["bot_name"]
            if room_id in self.rooms:
                self.rooms[room_id].dismiss(hint.no_enough_resource_info(bot_name))
                del self.rooms[room_id]
        gevent.sleep(1)

    @utils.run_forever
    @utils.catch_exception
    def recv_user(self):
        conn, addr = self.s.accept()
        logger.info("accept user {}:{}", addr[0], addr[1])
        gevent.spawn(self.recv_data_run, conn, addr)

    def recv_data_run(self, conn, addr):
        try:
            self.recv_data(conn, addr)
        except Exception as e:
            self.tear_down(conn, hint.unknown_error_info(repr(e)))
            logger.exception(e)

    def recv_data(self, conn, addr):
        data = utils.recvJson(conn)
        logger.info("{}:{}, {}", addr[0], addr[1], data)
        info = itemgetter("info")(data)
        
        if info == "connect":
            room_id, name, room_number, bots, game_number = itemgetter("room_id", "name", "room_number", "bots", "game_number")(data)
            room_id = int(room_id)
            room = self.get_room(room_id, room_number, game_number, bots)
            if room.full():
                self.tear_down(conn, hint.room_full_info(room_id))
                return
            room.add_player(conn, name)
            succ, agent_name = room.notify_bots(self.supported_agent, self.rb)
            if not succ:
                self.tear_down(conn, hint.agent_not_found_info(agent_name))
                del self.rooms[room_id]
                return 
            if room.full():
                self.controlers[room.control_id].dispatch(room)
        
        if info == "observer":
            room_id = int(itemgetter("room_id")(data))
            if room_id not in self.rooms:
                self.tear_down(conn, hint.room_not_exist_info(room_id))
                return
            room = self.rooms[room_id]
            self.controlers[room.control_id].dispatch_observer(conn, room_id)

        if info == "ai_vs_ai":
            room_id, room_number, bots, game_number = itemgetter("room_id", "room_number", "bots", "game_number")(data)
            room_id = int(room_id)
            room = self.get_room(room_id, room_number, game_number, bots, True)
            if room.full():
                self.tear_down(conn, hint.room_full_info(room_id))
                return
            succ, agent_name = room.notify_bots(self.supported_agent, self.rb)
            if not succ:
                self.tear_down(conn, hint.agent_not_found_info(agent_name))
                del self.rooms[room_id]
                return
            self.controlers[room.control_id].dispatch_observer(conn, room_id)
    
    def tear_down(self, conn, info=None):
        # logger.warning(info)
        if info is not None:
            utils.sendJson(conn, info)
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        conn.close()

    def get_room(self, room_id, room_number, game_number, bots, is_ai=False):
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(room_id, room_number, game_number, bots, self.cur_control, is_ai)
            self.cur_control += 1
            self.cur_control %= len(self.controlers)
        return self.rooms[room_id]

class Receiver(multiprocessing.Process):
    def __init__(self, room_end_queue, agent_error_queue):
        super().__init__()
        self.room_end_queue = room_end_queue
        self.agent_error_queue = agent_error_queue
        self.rb = rabbitmq.Rabbitmq()
        self.rb.recv_msg_from_queue('room_end_queue', self.room_end_callback)
        self.rb.recv_msg_from_queue("agent_error_queue", self.agent_error_call_back)
            
    def agent_error_call_back(self, ch, method, props, body):
        msg = json.loads(body)
        logger.info(msg)
        self.agent_error_queue.put(msg)

    def room_end_callback(self, ch, method, props, body):
        room_id = json.loads(body)[0]
        self.room_end_queue.put(room_id)
    
    def run(self):
        self.rb.start()

class DatabaseReceiver(multiprocessing.Process):
    def __init__(self):
        super().__init__()
        self.rb = rabbitmq.Rabbitmq()
        self.rb.recv_msg_from_queue("mysql_queue", self.callback)
        self.db = mysql.Mysql()

    def callback(self, ch, method, props, body):
        msg = json.loads(body)
        # ch.basic_ack(method.delivery_tag)
        self.db.save(msg)

    def run(self):
        self.rb.start()
    
def main():
    controlers = [
        WorkerControler()
        for i in range(cfg["num_workers"])
    ]
    room_end_queue = multiprocessing.Queue()
    agent_error_queue = multiprocessing.Queue()

    listener = Listener(cfg["server"]["host"], cfg["server"]["port"], controlers, room_end_queue, agent_error_queue)
    Receiver(room_end_queue, agent_error_queue).start()

    for i in range(cfg["num_database"]):
        DatabaseReceiver().start()

    listener.run()
                       
if __name__ == '__main__':
    main()