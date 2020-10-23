# from games.nolimitholdem.game import Game

# game = Game(4)

# player_id = game.game_init()

# while not game.is_terminal():
#     state = game.get_state(player_id)
#     print(state)
#     action = input("Action: ")
#     player_id = game.step(action)

from games.nolimitholdem.judge import *

hand_cards = ["As", "Ts"]
desktop_cards = ["3s", "4d", "5d", "2s", "Jh"]
print(best_cards(hand_cards, desktop_cards))