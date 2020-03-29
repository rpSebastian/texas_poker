import multiprocessing
from games.nolimitholdem.game import Game
from utils.utils import sendJson, recvJson
from core.card_tools import card_tools
from .lookup import lookup
from database.mysql import Mysql
import numpy as np
import copy
HC = 1326
CC = 52


class LocalBestResbonse(multiprocessing.Process):

    def __init__(self, client, method):
        super().__init__()
        self.opponent = client
        self.game = Game(2)
        # self.valid_raise = [0.5, 1, 20000]

        if method == 'lbr-fc-1-4':
            self.bet_round, self.valid_raise, self.name = [1, 2, 3, 4], [], 'lbr-fc-1-4'
        elif method == 'lbr-fc-3-4':
            self.bet_round, self.valid_raise, self.name = [3, 4], [], 'lbr-fc-3-4'
        elif method == 'lbr-fcpa-1-4':
            self.bet_round, self.valid_raise, self.name = [1, 2, 3, 4], [20000], 'lbr-fcpa-1-4'
        elif method == 'lbr-fcpa-3-4':
            self.bet_round, self.valid_raise, self.name = [3, 4], [20000], 'lbr-fcpa-3-4'
        else:
            sendJson(client.socket, {"info": "error", "text": "method not support!"})
            client.socket.close()
            raise Exception("method not support!")
        self.mysql = Mysql()

    def run(self):
        try:
            self.work()
        except Exception as e:
            # print(e)
            pass
            
    def work(self):
        self.lbr_id, self.opponent_id = 0, 1
        self.notify_name()
        while True:
            player_id = self.game.game_init()
            self.lbr_init()
            self.recv_start()
            while not self.game.is_terminal():
                self.notify_state()
                if player_id == self.lbr_id:
                    action = self.lbr_turn()
                else:
                    action = self.opponent_turn()
                player_id = self.game.step(action)
            self.notify_state(True)
            self.notify_result()
            self.save_data()
            self.lbr_id, self.opponent_id = self.opponent_id, self.lbr_id
    
    def save_data(self):
        message = self.game.get_save_data()
        message['name'] = [self.name, self.name]
        message['name'][self.opponent_id] = self.opponent.name
        message['position'] = [0, 1]
        self.mysql.save(message)
    
    def notify_state(self, last=False):
        state = self.game.get_state(self.opponent_id)
        state['info'] = 'state'
        if last:
            state['action_position'] = -1
        sendJson(self.opponent.socket, state)
      
    def notify_name(self):
        message = {}
        message['info'] = 'name'
        message['name'] = [self.name, self.name]
        message['name'][self.opponent_id] = self.opponent.name
        message['position'] = self.opponent_id
        sendJson(self.opponent.socket, message)    

    def notify_result(self):
        state = self.game.get_payoff()
        state['info'] = 'result'
        sendJson(self.opponent.socket, state)
        
    def recv_start(self):
        message = recvJson(self.opponent.socket)

    def lbr_init(self):
        """
            初始化对手range，解决与lbr手牌的冲突，对手range中lbr手牌对应位置的出现概率为0
        """
        self.opponent_range = np.ones(HC, dtype=np.float)
        state = self.game.get_state(self.lbr_id)
        self.private_card = state['private_card']
        for card in self.private_card:
            for card2_id in range(CC):
                card2 = card_tools.id_to_card(card2_id)
                if card == card2: continue
                self.opponent_range[card_tools.hand_to_id((card, card2))] = 0
        self.opponent_range /= sum(self.opponent_range)
        
    def lbr_turn(self):
        # print()
        # print('-------------------')
        state = self.game.get_state(self.lbr_id)
        round_number = len(state['action_history'])
        if not round_number in self.bet_round:
            if 'call' in state['legal_actions']:
                action = 'call'
            else:
                action = 'check'
            return action
        # print(state)
        if self.check_round_start(state):
            self.public_card_conflict(state)
        wp = self.wp_rollout(state['private_card'], state['public_card'], self.opponent_range)
        opponent_bet, lbr_bet = self.get_bets(state)
        utility = np.zeros(len(self.valid_raise) + 2)
        utility[-2] = wp * opponent_bet - (1 - wp) * opponent_bet
        utility[-1] = -lbr_bet
        if 'raise' in state['legal_actions']:
            for i, raise_ratio in enumerate(self.valid_raise):
                # 获取lbr在执行raise动作后，对手在不同手牌下的fold概率
                amount = self.calc_amount(raise_ratio, state)
                fold_prop = self.get_fold_prop(amount)
                # 计算执行raise动作后，对手fold的概率和不fold下的新range
                fp = np.sum(self.opponent_range * fold_prop)
                new_opponent_range = self.opponent_range * (1 - fold_prop)
                new_opponent_range /= np.sum(new_opponent_range)
                wp = self.wp_rollout(state['private_card'], state['public_card'], new_opponent_range) # TODO 修改为执行动作a后的
                utility[i] = fp * opponent_bet + (1 - fp) * (wp * amount - (1 - wp) * amount)
        else:
            utility[:-2] = -200000
        index = np.argmax(utility)
        if index == len(self.valid_raise):
            if 'call' in state['legal_actions']:
                action = 'call'
            else:
                action = 'check'
        elif index == len(self.valid_raise) + 1:
            action = 'fold'
        else:
            amount = self.calc_amount(self.valid_raise[index], state)
            round_raised = self.get_round_raised(state['action_history'])
            action = 'r' + str(amount - sum(round_raised[:-1]))
        return action

    def opponent_turn(self):
        """
            对手执行动作，通过通信协议获取对手动作和策略，并更新
        """
        state = self.game.get_state(self.opponent_id)
        if self.check_round_start(state):
            self.public_card_conflict(state)
        strategy, action = self.recv_action()
        self.opponent_range *= strategy
        self.opponent_range /= np.sum(self.opponent_range)
        return action

    def calc_amount(self, raise_ratio, state):
        """
            通过下注比例计算本轮的下注量
        """
        round_raised = self.get_round_raised(state['action_history'])
        min_bet = sum(round_raised[:-1]) + state['raise_range'][0]
        max_bet = sum(round_raised[:-1]) + state['raise_range'][1]
        amount = int(sum(round_raised) * (1 + 2 * raise_ratio))
        amount = min(amount, max_bet)
        amount = max(amount, min_bet)
        return amount

    def get_bets(self, state):
        """
            通过动作序列计算得到对手和lbr的总下注量
       
        """
        round_raised = self.get_round_raised(state['action_history'])
        opponent_bet = self.get_current_round_bet(self.opponent_id, state['action_history']) + sum(round_raised[:-1])
        lbr_bet = self.get_current_round_bet(self.lbr_id, state['action_history']) + sum(round_raised[:-1])
        return opponent_bet, lbr_bet

    def get_current_round_bet(self, position, action_history):
        actions = action_history[-1].copy()
        if len(action_history) == 1:
            actions.insert(0, '1:r100')
            actions.insert(0, '0:r50')
        pmax = None
        for action in reversed(actions):
            p, a = action.split(':')
            if int(p) == position and a[0] == 'r' and pmax is None:
                return int(a[1:])
            if int(p) == position and a[0] == 'c' and pmax is None:
                pmax = 0
            if pmax is not None and a[0]=='r':
                pmax = max(pmax, int(a[1:]))
        if pmax == None:
            pmax = 0
        return pmax

    def get_round_raised(self, action_history):
        result = []
        for i, one_round in enumerate(action_history):
            rmax = 0
            if i == 0:
                rmax = 100
            for one_action in one_round:
                p, a = one_action.split(":")
                if a[0] == "r":
                    rmax = max(rmax, int(a[1:]))
            result.append(rmax)
        return result 


    def wp_rollout(self, private_card, public_card, opponent_range):
        """
            双方都执行call/check到最后一轮，根据对手range计算lbr获胜的概率。
        """
        # return 0.8
        return lookup.calc(private_card, public_card, opponent_range)
        # print(wp)
        # wp = 0.5
        # leave_cards = []
        # for i in range(CC):
        #     if not card_tools.id_to_card(i) in private_card and not card_tools.id_to_card(i) in public_card:
        #         leave_cards.append(i)
        # self.outcome = 0    
        # self.num = 0
        # self.enumerate_leave_public_card(-1, leave_cards, private_card, public_card, opponent_range)
        # total = 1
        # for i in range(CC - len(private_card) - len(public_card)):
        #     total *= 52 - i
        # for i in range(CC - len(private_card) - len(public_card)):
        #     total /= (i + 1)
        # wp = self.outcome / total
        # print(self.outcome, total)
    # def calc_win_probablity(self, private_card, public_card, opponent_range):
        # new_opponent_range = opponent_range.copy()
        # for card in public_card:
        #     for card2_id in range(CC):
        #         card2 = card_tools.id_to_card(card2_id)
        #         if card == card2: continue
        #         new_opponent_range[card_tools.hand_to_id((card, card2))] = 0
        # new_opponent_range /= sum(new_opponent_range)

        # hands = np.zeros([HC, 7], dtype=np.int)
        # board = np.array([card_tools.card_to_id(card) for card in public_card], dtype=np.int)
        # hands[: ,  :5 ] = np.repeat(board.reshape([1, 5]), HC, axis=0)
        # hands[: , 5:7 ] = card_tools.hand_ids
        # hands_strength = card_tools.evaluate(hands)
        # lbr_hand = np.array([[card_tools.card_to_id(card) for card in (*public_card, *private_card)]], dtype=np.int)
        # lbr_strength = card_tools.evaluate(lbr_hand)
        # result = (lbr_strength > hands_strength).astype(np.int) 
        # self.outcome += np.dot(result, opponent_range)
    
    def get_fold_prop(self, amount):
        """
            根据通信协议发送给对手lbr的动作，要求返回不同手牌下fold的概率，并且此次询问是临时询问
        """
        state = self.game.get_state(self.opponent_id)
        round_raised = self.get_round_raised(state["action_history"])
        amount -= sum(round_raised[:-1])
        state['info'] = 'fold_strategy'
        state['action_position'] = self.opponent_id
        state['action_history'] = copy.deepcopy(state['action_history'])
        state["action_history"][-1].append(str(self.lbr_id) + ":"+"r"+str(amount))
        state['legal_actions'], state['raise_range'] = self.calc_legal(state['action_history'])
        sendJson(self.opponent.socket, state)
        message = recvJson(self.opponent.socket)
        fold_strategy = np.array(message['strategy'], dtype=np.float)
        return fold_strategy
    
    def calc_legal(self, action_history):
        round_raised = self.get_round_raised(action_history)
        opponent_bet = self.get_current_round_bet(self.opponent_id, action_history) + sum(round_raised[:-1])
        lbr_bet = self.get_current_round_bet(self.lbr_id, action_history) + sum(round_raised[:-1])
        legal_actions = ['call', 'fold']
        raise_range = None
        if lbr_bet != 20000:
            legal_actions.append('raise')
            max_raise = 20000
            min_raise = lbr_bet + max(100, lbr_bet - opponent_bet)
            min_raise = min(20000, min_raise)
            raise_range = [min_raise - sum(round_raised[:-1]), max_raise - sum(round_raised[:-1])]
        return legal_actions, raise_range

    def recv_action(self):
        """
            在对手执行动作时，向对手发送状态，接收对手的动作，以及在各种手牌下执行该动作的概率。
        """
        message = recvJson(self.opponent.socket)
        action = message['action']
        strategy = np.array(message['strategy'], dtype=np.float)
        return strategy, action

    def check_round_start(self, state):
        """
            判断是否每轮的开始
        """
        action_history = state['action_history']
        return len(action_history) >= 2 and len(action_history[-1]) == 0
    
    def public_card_conflict(self, state):
        """
            在每一轮的开始发完公共牌后，解决与对手range的冲突，对手range中公共牌对应位置的出现概率为0
        """
        card_number = [0, 3, 4, 5]
        current_round = len(state["action_history"])
        public_card = state['public_card']
        for i in range(card_number[max(0, current_round - 2)], card_number[current_round - 1]):
            card = public_card[i]
            for card2_id in range(CC):
                card2 = card_tools.id_to_card(card2_id)
                if card == card2: continue
                self.opponent_range[card_tools.hand_to_id((card, card2))] = 0
        self.opponent_range /= np.sum(self.opponent_range)
    
