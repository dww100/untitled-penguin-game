import logging
from penguin_game.game import Game

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":

    g = Game()
    while True:
        g.setup_play()
        g.run()
