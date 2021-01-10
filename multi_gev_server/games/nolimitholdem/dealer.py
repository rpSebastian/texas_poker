from core.deck import Deck


class Dealer():
    draw_card_number = [0, 3, 1, 1]

    def __init__(self, deck_id=None):
        self.deck = Deck(deck_id)
        self.pot = 0
        self.hands = []

    def deal_cards(self, number):
        return self.deck.deal_cards(number)
