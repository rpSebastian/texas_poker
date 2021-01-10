import random
from .card import Card

class Deck():

    ranks = [str(n) for n in range(2, 10)] + list('TJQKA')
    suits = list('shcd')

    def __init__(self, deck_id=None):
        file_name = "core/deck_file.txt"
        self.deck_list = []
        with open(file_name) as f:
            self.deck_list = [list(map(lambda s: s.strip(), line.split(','))) for line in f]

        if deck_id is None:    
            self.reset()
        else:
            self._cards = [Card(rank, suit) for rank, suit in self.deck_list[deck_id]]

    def reset(self):
        self._cards = [Card(rank, suit) for rank in self.ranks for suit in self.suits]
        random.shuffle(self._cards)

    def deal_cards(self, number):
        cards = []
        for _ in range(number):
            card = self._cards.pop(0)
            cards.append(card)
        return cards

