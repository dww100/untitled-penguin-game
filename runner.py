import logging
from penguin_game.game import Game
import pygame

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    pygame.mixer.init()
    pygame.mixer.music.load('sounds/theme.wav')
    pygame.mixer.music.play()

    g = Game()
    g.run()
