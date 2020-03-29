from .dealer import Dealer
from .player import Player
from .round import Round
from .judge import Judge
from datetime import datetime

class Game():

    def __init__(self, num_players):
        self.num_players = num_players
        self.stack = 20000
        self.small_blind = 50
        self.big_blind = 100
        self.judge = Judge()

    def game_init(self):
        self.dealer = Dealer()
        self.players = [Player(self.stack) for _ in range(self.num_players)]
        self.action_history = []
        for player in self.players:
            player.hands += self.dealer.deal_cards(2)
        self.round_counter = 0
        self.players[0].wager(50, self.dealer)
        self.players[1].wager(100, self.dealer)
        self.cur_round = Round(self.num_players, self.big_blind)
        self.action_history.append([])
        self.pointer = 2 % self.num_players
        self.action_player = ""
        self.current_action = ""
        self.cur_round.round_init(self.pointer, [50, 100] + [0 for _ in range(self.num_players - 2)])
        return self.pointer

    def step(self, action):
        if not self.check_action_valid(action):
            raise Exception("Action invalid!")
        self.action_player, self.current_action = self.pointer, action
        self.action_history[self.round_counter].append(dict(position=self.pointer, action=action, timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]))
        self.pointer = self.cur_round.step(self.players, self.dealer, action)
        if self.is_terminal():
            if self.is_terminal() == 3:
                while self.round_counter < 3:
                    self.dealer.hands += self.dealer.deal_cards([3, 1, 1][self.round_counter])
                    self.round_counter += 1
        elif self.cur_round.is_terminal():
            if self.round_counter != 3:
                self.dealer.hands += self.dealer.deal_cards([3, 1, 1][self.round_counter])
                self.round_counter += 1
                self.action_history.append([])
                self.pointer = 1
                self.skip_folded_player()
                self.cur_round.round_init(self.pointer)
        return self.pointer

    def skip_folded_player(self):
        while self.players[self.pointer].status == 'folded':
            self.pointer = (self.pointer + 1) % self.num_players

    def check_action_valid(self, action):
        legal_actions, raise_range = self.cur_round.get_legal_actions(self.players)
        if action[0] == 'r' and 'raise' in legal_actions \
           and int(action[1:]) >= raise_range[0] \
           and int(action[1:]) <= raise_range[1]:
            return True
        if action in legal_actions:
            return True
        return False

    def is_terminal(self):
        # 其他人都fold了
        if sum(player.status == 'alive' for player in self.players) == 1:
            return 1
        # 4轮叫牌结束了
        if self.round_counter == 3 and self.cur_round.is_terminal():
            return 2
    # 所有人all in了
        if max(player.remained_chips for player in self.players if player.status == "alive") == 0:
            return 3
        return 0

    def get_payoff(self):
        state = {}
        win_money = self.judge.get_payoff(self.players, self.dealer, self.stack)
        if self.is_terminal() == 1:
            state['player_card'] = [[] for player in self.players]
        else:
            state['player_card'] = [[str(card) for card in player.hands] if player.status == "alive"
                                    else [] for player in self.players]
        state['public_card'] = [str(card) for card in self.dealer.hands]
        state['action_history'] = self.action_history
        state["players"] = []
        for i, player in enumerate(self.players):
            player_info = {}
            player_info["position"] = i
            player_info["win_money"] = win_money[i]
            player_info["moneyLeft"] = player.remained_chips
            player_info["totalMoney"] = self.stack
            state['players'].append(player_info)
        return state

    def get_state(self, player_id):
        state = {}
        state["position"] = player_id
        state["action_position"] = self.pointer
        state["legal_actions"], state["raise_range"] = self.cur_round.get_legal_actions(self.players)
        state["private_card"] = [str(card) for card in self.players[player_id].hands]
        state["public_card"] = [str(card) for card in self.dealer.hands]
        state["players"] = []
        for i, player in enumerate(self.players):
            player_info = {}
            player_info["position"] = i
            player_info["money_left"] = player.remained_chips
            player_info["total_money"] = self.stack
            state['players'].append(player_info)
        state['action_history'] = self.action_history
        return state

    def get_public_state(self):
        state = {}
        state["action_position"] = self.pointer
        state["player_card"] = [[str(card) for card in player.hands] for player in self.players]
        state["public_card"] = [str(card) for card in self.dealer.hands]
        state["round_raise"] = self.cur_round.raised_counter
        state["current_action"] = self.current_action
        state["action_player"] = self.action_player
        state["action_history"] = self.action_history
        state["players"] = []
        for i, player in enumerate(self.players):
            player_info = {}
            player_info["position"] = i
            player_info["money_left"] = player.remained_chips
            player_info["total_money"] = self.stack
            state['players'].append(player_info)
        return state

    def get_save_data(self):
        state = {}
        state["public_card"] = [str(card) for card in self.dealer.hands]
        state["action_history"] = self.action_history
        state['player_card'] = [[str(card) for card in player.hands] for player in self.players]
        state["win_money"] = self.judge.get_payoff(self.players, self.dealer, self.stack)
        return state
