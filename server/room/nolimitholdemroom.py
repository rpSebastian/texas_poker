import copy
import random
from room import Room
from games.nolimitholdem.game import Game
from logs import logger
from err import MyError, PlayCompeleteError, PlayerExitError


class NoLimitHoldemRoom(Room):

    def init(self):
        random.shuffle(self.clients)
        self.game_count = 0
        self.ready_count = 0
        self.game = Game(self.room_number)
        self.init_game()

    def init_game(self):
        self.current_player_id = self.game.game_init()
        if self.mode == "duplicate":
            if self.game_count % 2 == 0:
                self.record_game = copy.deepcopy(self.game)
                self.record_player = self.current_player_id
            else:
                self.game = self.record_game
                self.current_player_id = self.record_player
        self.notify_state()    
        
    def handle(self, uuid, data):
        try:
            if data['info'] == 'ready':
                self.handle_start_message(uuid, data)
            elif data['info'] == 'action':
                self.handle_action_message(uuid, data)
        except MyError as e:
            self.room_manager.send_logs(e.text)
        except Exception as e:
            logger.exception(e)

    def handle_start_message(self, uuid, data):
        status = data['status']
        if status == 'exit':
            raise PlayerExitError(self.room_id)
        self.ready_count += 1
        if self.ready_count == self.room_number:
            self.init_game()

    def handle_action_message(self, uuid, data):
        player_id = self.get_player_id(uuid)
        if player_id != self.current_player_id:
            raise Exception('Not your turn')
        action = data['action']
        self.current_player_id = self.game.step(action)
        if self.game.is_terminal():
            self.notify_state(last=True)
            self.notify_result()
            self.save_data()
            self.ready_count = 0
            self.game_count += 1
            logger.info("room {} finish game {}", self.room_id, self.game_count)
            if self.game_count == self.game_number:
                raise PlayCompeleteError(self.room_id)
            client = self.clients.pop(0)
            self.clients.append(client)
        else:
            self.notify_state()

    def save_data(self):
        message = self.game.get_save_data()
        message['name'] = [client.name for client in self.clients]
        message['position'] = [i for i in range(len(self.clients))]
        message['room_id'] = self.room_id
        self.mysql.save(message)

    def notify_state(self, last=False):
        for i, client in enumerate(self.clients):
            state = self.game.get_state(i)
            for j, player in enumerate(self.clients):
                state['players'][j]['name'] = player.name
            state['info'] = 'state'
            if last:
                state['action_position'] = -1
            self.room_manager.send_message(state, room_id=self.room_id, receiver='player', uuid=client.uuid)            

        state = self.game.get_public_state()
        if last:
            state['action_position'] = -1
        state['info'] = 'state'
        for i, player in enumerate(self.clients):
            state['players'][i]['name'] = player.name
        self.room_manager.send_message(state, room_id=self.room_id, receiver='observer')

    def notify_result(self):
        for i, client in enumerate(self.clients):
            state = self.game.get_payoff(i)
            state['info'] = 'result'
            for j, player in enumerate(self.clients):
                state['players'][j]['name'] = player.name
            self.room_manager.send_message(state, room_id=self.room_id, receiver='player', uuid=client.uuid)
            client.update_session(state['players'][i]['win_money'])
        state = self.game.get_payoff()
        state['info'] = 'result'
        state['total_money'] = [client.session for client in self.clients]
        state['times'] = [client.times for client in self.clients]
        for i, player in enumerate(self.clients):
            state['players'][i]['name'] = player.name
        self.room_manager.send_message(state, room_id=self.room_id, receiver='observer')

    def get_player_id(self, uuid):
        player_id = None
        for i, client in enumerate(self.clients):
            if uuid == client.uuid:
                player_id = i
        return player_id
