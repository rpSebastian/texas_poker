class Card():
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return self.rank + self.suit

    def __repr__(self):
        return f'Card(rank={self.rank}, suit={self.suit})'

    def __lt__(self, other):
        trans = {**{str(i): i for i in range(2, 10)}, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return trans[self.rank] < trans[other.rank] or trans[self.rank] == trans[other.rank] and self.suit < other.suit
