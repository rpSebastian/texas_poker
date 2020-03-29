import random
from .card import Card


class Deck():

    ranks = [str(n) for n in range(2, 10)] + list('TJQKA')
    suits = list('shcd')

    def __init__(self):
        # random.seed(0)
        self.reset()

    def reset(self):
        self._cards = [Card(rank, suit) for rank in self.ranks for suit in self.suits]
        random.shuffle(self._cards)

    def deal_cards(self, number):
        cards = []
        for _ in range(number):
            card = self._cards.pop()
            cards.append(card)
        return cards
