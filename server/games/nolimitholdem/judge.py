import copy
import itertools
import collections
from core.card import Card


class Judge():
    def get_payoff(self, players, dealer, stack):
        valid_num = sum(player.status == 'alive' for player in players)
        payoff = []
        if valid_num == 1:
            for player in players:
                win_money = player.remained_chips - stack
                if player.status == 'alive':
                    win_money += dealer.pot
                payoff.append(win_money)
        else:
            for player in players:
                player.hand_level = hand_level(player.hands, dealer.hands)
            max_level = max(player.hand_level for player in players if player.status == 'alive')
            for player in players:
                player.winner = player.status == 'alive' and player.hand_level == max_level
            win_num = sum(player.winner for player in players)
            for player in players:
                win_money = player.remained_chips - stack
                if player.winner:
                    win_money += dealer.pot / win_num
                payoff.append(win_money)
        return payoff


def hand_level(hand_cards, desktop_cards):
    '''输入手牌和桌牌，计算最大的牌面

    在2张手牌和5张桌牌中进行组合，计算得出最大的牌面，牌面用元组进行表示。两个牌面可以直接进行比较。
    牌型级别为:
        9->同花顺， 8->四条， 7->葫芦， 6->同花, 5->顺子,
        4->三条， 3->两对， 2->一对, 1->高牌

    Args:
        hand_cards: 手牌，2张牌的列表
        desktop_cards: 桌牌，5张牌的列表

    Returns:
        一个元组表示最大牌面，第一个元素为牌型，剩下元素为相同牌型下依次比较的牌。
    '''
    total_cards = [*hand_cards, *desktop_cards]
    if isinstance(total_cards[0], str):
        total_card = []
        for card in total_cards:
            total_card.append(Card(card[0], card[1]))
        total_cards = total_card
    cards_iter = itertools.combinations(total_cards, 5)
    best_cards = max(cards_iter, key=lambda x: cards_level(x))
    return cards_level(best_cards)


def cards_level(cards):
    cards = list(copy.deepcopy(cards))
    trans = {**{str(i): i for i in range(2, 10)}, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    for card in cards:
        card.rank = trans[card.rank]
    cards.sort(key=lambda x: x.rank, reverse=True)
    num = collections.defaultdict(int)
    for card in cards:
        num[card.rank] += 1
    item = collections.namedtuple('counter_item', ('rank', 'times'))
    count = sorted([item(key, value) for key, value in num.items()], key=lambda x: (x.times, x.rank), reverse=True)
    level = enumerate_level(cards, count)
    return level


def enumerate_level(cards, count):
    results = []
    results.append(straight_flush(cards))
    results.append(four_of_a_kind(count))
    results.append(full_house(count))
    results.append(flush(cards))
    results.append(straight(cards))
    results.append(three_of_a_kind(count))
    results.append(two_pair(count))
    results.append(one_pair(count))
    results.append(high_card(count))
    for succ, *level in results:
        if succ:
            return (*level, )


def straight_flush(cards):
    for i in range(4):
        if cards[i].suit != cards[i + 1].suit or cards[i].rank != cards[i + 1].rank + 1:
            return (False, )
    return (True, 9, cards[0].rank)


def four_of_a_kind(count):
    if count[0].times == 4:
        return (True, 8, *(n.rank for n in count))
    return (False, )


def full_house(count):
    if count[0].times == 3 and count[1].times == 2:
        return (True, 7, *(n.rank for n in count))
    return (False, )


def flush(cards):
    for i in range(4):
        if cards[i].suit != cards[i + 1].suit:
            return (False, )
    return (True, 6, *(n.rank for n in cards))


def straight(cards):
    for i in range(4):
        if cards[i].rank != cards[i + 1].rank + 1:
            return (False, )
    return (True, 5, cards[0].rank)


def three_of_a_kind(count):
    if count[0].times == 3 and len(count) == 3:
        return (True, 4, *(n.rank for n in count))
    return (False, )


def two_pair(count):
    if count[0].times == 2 and count[1].times == 2:
        return (True, 3, *(n.rank for n in count))
    return (False, )


def one_pair(count):
    if count[0].times == 2 and len(count) == 4:
        return (True, 2, *(n.rank for n in count))
    return (False, )


def high_card(count):
    if len(count) == 5:
        return (True, 1, *(n.rank for n in count))
    return (False, )
