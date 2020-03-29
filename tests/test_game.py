import os
import sys
os.chdir('..')
sys.path.append( os.path.join(os.getcwd()) )

from poker_server.games.nolimitholdem.game import Game

game = Game(3)

player_id = game.game_init()

while True:
    if game.is_terminal():
        print(game.get_payoff())
        break
    else:
        print(game.get_state(player_id))
        a = input()
        player_id = game.step(a)
    