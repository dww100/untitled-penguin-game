from __future__ import annotations

from typing import Union, List
import pygame as pg
from pygame.math import Vector2

from .settings import PLAYER_SPEED, RED
from .entities import Actor


class Block(Actor):
    def __init__(
        self,
        game: "penguin_game.game.Game",
        x: int,
        y: int,
    ) -> None:
        """Block Sprite.

        Args:
            game: Game that this Sprite is associated with (provides access to timing, etc).
            x: Horizontal starting position in pixels.
            y: Vertical starting position in pixels.
        """
        super().__init__(game, x, y, additional_groups=game.blocks)
        self.image.fill(RED)


class Player(Actor):
    def __init__(
        self,
        game: "penguin_game.game.Game",
        x: int,
        y: int,
    ) -> None:
        """Player Sprite.

        Args:
            game: Game that this Sprite is associated with (provides access to timing, etc).
            x: Horizontal starting position in pixels.
            y: Vertical starting position in pixels.
        """
        super().__init__(game, x, y, additional_groups=game.player)
        self.stopped_by.append(game.blocks)
        # Start facing left
        self.facing = Vector2(-1, 0)

    def get_keys(self) -> None:
        """Handle keyboard input.
        """
        self.vel = Vector2(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.facing = Vector2(-1, 0)
            self.vel = self.facing * PLAYER_SPEED
        if keys[pg.K_RIGHT]:
            self.facing = Vector2(1, 0)
            self.vel = self.facing * PLAYER_SPEED
        if keys[pg.K_UP]:
            self.facing = Vector2(0, -1)
            self.vel = self.facing * PLAYER_SPEED
        if keys[pg.K_DOWN]:
            self.facing = Vector2(0, 1)
            self.vel = self.facing * PLAYER_SPEED
        if keys[pg.K_SPACE]:
            self.fire()

    def fire(self):
        pass

    def update(self) -> None:
        """Update state each time round the game loop.
        Checks for user input, then handles movement and wall collisions.

        """
        self.get_keys()
        super().update()


class Enemy(Actor):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
