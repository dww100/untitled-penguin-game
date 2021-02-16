import logging
from penguin_game.game import Game

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":

    g = Game()
    g.run()
