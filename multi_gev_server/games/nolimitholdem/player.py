class Player():
    def __init__(self, stack):
        self.remained_chips = stack
        self.hands = []
        self.status = 'alive'

    def wager(self, amount, dealer):
        self.remained_chips -= amount
        dealer.pot += amount
        



