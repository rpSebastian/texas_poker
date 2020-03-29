import os
import numpy as np
from core.card_tools import card_tools


class Lookup():

    def __init__(self):
        self.random_board_wp = np.load("./eval/random_board_wp.npy")

    def check(self, a, b):
        if b == None or a == None:
            return False
        for x in a:
            if x in b:
                return True
        return False

    def find(self, hand1, hand2, board = None):
        # print(hand1, hand2, boarsd)
        if board == []:
            board = None
        if (self.check(hand1, hand2) or self.check(hand1, board) or self.check(hand2, board)):
            # raise Exception("same card!")
            return 0
        if board == None:
            # hand_str1 = ''.join(hand1)
            # hand_str2 = ''.join(hand2)
            # command = "./poker_server/eval/ps-eval " + hand_str1 + " " + hand_str2 
            # print(command)
            # a = os.popen(command).read().split("\n")
            # wp = float(a[0].split(' ')[4]) / 100
            wp = self.random_board_wp[card_tools.hand_to_id(hand1), card_tools.hand_to_id(hand2)]
            assert(wp > 0)
            # print(wp, wp2)
            # assert(wp == wp2)
        else:
            hand_str1 = ''.join(hand1)
            hand_str2 = ''.join(hand2)
            board_str = ''.join(board)
            command = "./poker_server/eval/ps-eval " + hand_str1 + " " + hand_str2  + " --board " + board_str
            a = os.popen(command).read().split("\n")
            wp = float(a[0].split(' ')[4]) / 100
        return wp

    def calc(self, hand1, board, opponent_range):
        if len(board) == 0:
            return self.calc2(hand1, board, opponent_range)
        else:
            return self.calc1(hand1, board, opponent_range)

    def calc2(self, hand1, board, opponent_range):
        wp = 0
        for hid in range(1326):
            if opponent_range[hid] == 0: continue
            opponent_card = card_tools.id_to_hand(hid)
            wp += self.find(hand1, opponent_card, board) * opponent_range[hid]
        return wp 

    def calc1(self, hand1, board, opponent_range):
        leave_cards = []
        for i in range(52):
            if not card_tools.id_to_card(i) in hand1 and not card_tools.id_to_card(i) in board:
                leave_cards.append(i)
        self.outcome = 0
        self.enumerate_leave_public_card(-1, leave_cards, hand1, board, opponent_range)
        total = 1
        for i in range(5 - len(board)):
            total *= len(leave_cards) - i
        for i in range(5 - len(board)):
            total /= (i + 1)
        self.outcome /= total
        return self.outcome

    def enumerate_leave_public_card(self, start_index, leave_cards, hand, board, opponent_range):
        if len(board) == 5:
            self.calc_win_probablity(hand, board, opponent_range)
            return 
        for i in range(start_index + 1, len(leave_cards)):
            board.append(card_tools.id_to_card(leave_cards[i]))
            self.enumerate_leave_public_card(i, leave_cards, hand, board, opponent_range)
            board.pop()

    def calc_win_probablity(self, private_card, public_card, opponent_range):
        # print(private_card, public_card)
        # print(opponent_range)
        new_opponent_range = opponent_range.copy()
        for card in public_card:
            for card2_id in range(52):
                card2 = card_tools.id_to_card(card2_id)
                if card == card2: continue
                new_opponent_range[card_tools.hand_to_id((card, card2))] = 0
        new_opponent_range /= sum(new_opponent_range)

        hands = np.zeros([1326, 7], dtype=np.int)
        board = np.array([card_tools.card_to_id(card) for card in public_card], dtype=np.int)
        hands[: ,  :5 ] = np.repeat(board.reshape([1, 5]), 1326, axis=0)
        hands[: , 5:7 ] = card_tools.hand_ids
        hands_strength = card_tools.evaluate(hands)
        lbr_hand = np.array([[card_tools.card_to_id(card) for card in (*public_card, *private_card)]], dtype=np.int)
        lbr_strength = card_tools.evaluate(lbr_hand)
        result = (lbr_strength > hands_strength).astype(np.float) + (lbr_strength == hands_strength).astype(np.float) * 0.5
        np.set_printoptions(threshold = 1e6)
        # print(lbr_strength)
        # print(hands_strength)
        # print(opponent_range)
        # print(result * opponent_range)
        self.outcome += np.dot(result, new_opponent_range)
        # print(result)

lookup = Lookup()


# import time 
# a = time.time()
# hand1 = ['Kc', 'Jh']
# board = ['5c', '4c', 'Ac']
# opponent_range = np.array([1 for i in range(1326)], dtype=np.float)
# for card in (*hand1, *board):
#     for card2_id in range(52):
#         card2 = card_tools.id_to_card(card2_id)
#         if card == card2: continue
#         opponent_range[card_tools.hand_to_id((card, card2))] = 0
# print(np.sum(opponent_range))
# opponent_range /= np.sum(opponent_range)
# print(opponent_range)
# print(lookup.calc(hand1, board, opponent_range))
# print(lookup.calc2(hand1, board, opponent_range))

# print(opponent_range)
# for i in range(1326):
#     hand2 = card_tools.id_to_hand(i)
#     lookup.find(hand1, hand2, board)
#     result = lookup.find(hand1, hand2, board)
#     if result > 0: 
#         print(hand1, hand2, board, result)

# print(time.time() - a)