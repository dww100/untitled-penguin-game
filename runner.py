import logging
from penguin_game.game import Game
import pygame

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    pygame.mixer.init()
    pygame.mixer.music.load('penguin-game/sounds/sounds/theme.wav')
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1, fade_ms=1000)

    g = Game()
    g.run()
