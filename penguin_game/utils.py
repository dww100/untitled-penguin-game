import pygame as pg

def play_sound(sound):
    if pg.mixer.Channel(sound[1]).get_busy():
        pg.mixer.Channel(sound[1]).stop()
    pg.mixer.Channel(sound[1]).play(sound[0])

class SpriteSheet:
    def __init__(self):
        pass
