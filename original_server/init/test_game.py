import copy
import context

from games.nolimitholdem.game import Game

game = Game(2)
player = game.game_init()

game_2 = copy.deepcopy(game)
player_2 = player

while not game.is_terminal():
    state = game.get_state(player)
    legal_actions = state["legal_actions"]
    if "check" in legal_actions:
        action = "check"
    else:
        action = "call"
    player = game.step(action)
    print(state["public_card"])
        

game = game_2
player = player_2


while not game.is_terminal():
    state = game.get_state(player)
    legal_actions = state["legal_actions"]
    if "check" in legal_actions:
        action = "check"
    else:
        action = "call"
    player = game.step(action)
    print(state["public_card"])
