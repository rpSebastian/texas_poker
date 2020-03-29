import multiprocessing
from games.nolimitholdem.game import Game
from utils.utils import sendJson, recvJson, DisconnectException
from database.mysql import Mysql
from logs import logger
import socket
import random
import struct


class NoLimitHoldemKernel(multiprocessing.Process):
    def __init__(self, clients, observer_queue):
        super().__init__()
        self.clients = clients
        self.game = Game(len(self.clients))
        self.counter = 0
        self.observer_queue = observer_queue
        self.observers = []
        for client in self.clients:
            client.socket.settimeout(300)
        self.mysql = Mysql()

    def run(self):
        try:
            self.work()
        except (socket.timeout, BrokenPipeError, struct.error, socket.error, DisconnectException):
            pass
        except Exception as e:
            logger.exception(e)
        finally:
            self.mysql.end()
            for client in self.clients:
                try:
                    client.socket.shutdown(socket.SHUT_RDWR)
                    client.socket.close()
                except Exception:
                    pass
            for observer in self.observers:
                try:
                    observer.socket.shutdown(socket.SHUT_RDWR)
                    observer.socket.close()
                except Exception:
                    pass

    def work(self):
        random.shuffle(self.clients)
        self.notify_name()
        while True:
            while not self.observer_queue.empty():
                self.observers.append(self.observer_queue.get())
            player_id = self.game.game_init()
            self.counter += 1
            self.recv_start()
            while not self.game.is_terminal():
                self.notify_state()
                for i, client in enumerate(self.clients):
                    if player_id == i:
                        message = recvJson(client.socket)
                        action = message['action']
                player_id = self.game.step(action)
            self.notify_state(True)
            while not self.observer_queue.empty():
                self.observers.append(self.observer_queue.get())
            self.notify_result()
            self.save_data()
            client = self.clients.pop(0)
            self.clients.append(client)

    def save_data(self):
        message = self.game.get_save_data()
        message['name'] = [client.name for client in self.clients]
        message['position'] = [i for i in range(len(self.clients))]
        self.mysql.save(message)

    def recv_start(self):
        for client in self.clients:
            recvJson(client.socket)

    def notify_name(self):
        for i, client in enumerate(self.clients):
            message = self.name_message(i)
            sendJson(client.socket, message)

    def name_message(self, i):
        message = {}
        message['info'] = 'name'
        message['name'] = [client.name for client in self.clients]
        message['position'] = i
        return message

    def notify_result(self):
        for i, client in enumerate(self.clients):
            state = self.game.get_payoff()
            state['info'] = 'result'
            sendJson(client.socket, state)
            client.update_session(state['win_money'][i])

        disconnect_observer = []
        for observer in self.observers:
            try:
                state = self.game.get_payoff()
                state['info'] = 'result'
                state['total_money'] = [client.session for client in self.clients]
                state['times'] = [client.times for client in self.clients]
                state['name'] = [client.name for client in self.clients]
                sendJson(observer, state)
            except Exception:
                disconnect_observer.append(observer)
        for observer in disconnect_observer:
            self.observers.remove(observer)

    def notify_state(self, last=False):
        for i, client in enumerate(self.clients):
            state = self.game.get_state(i)
            state['info'] = 'state'
            if last:
                state['action_position'] = -1
            sendJson(client.socket, state)

        disconnect_observer = []
        for observer in self.observers:
            try:
                state = self.game.get_public_state()
                if last:
                    state['action_position'] = -1
                state['info'] = 'state'
                state['name'] = [client.name for client in self.clients]
                sendJson(observer, state)
            except Exception as e:
                disconnect_observer.append(observer)
        for observer in disconnect_observer:
            self.observers.remove(observer)
