from __future__ import annotations

from typing import Union, List
import pygame as pg

from .settings import PLAYER_SPEED
from .entities import Actor


class Player(Actor):
    def __init__(
        self,
        game: "penguin_game.game.Game",
        x: int,
        y: int,
        additional_groups: Union[pg.sprite.Group, List[pg.sprite.Group], None] = None,
    ) -> None:
        """Player Sprite.

        Args:
            game: Game that this Sprite is associated with (provides access to timing, etc).
            x: Horizontal starting position in pixels.
            y: Vertical starting position in pixels.
            additional_groups: Sprite groups other than `game.all_sprites` to be associated with.
        """
        super().__init__(game, x, y, additional_groups=additional_groups)

    def get_keys(self) -> None:
        """Handle keyboard input.
        """
        self.vx, self.vy = 0, 0
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.vx = -PLAYER_SPEED
        if keys[pg.K_RIGHT]:
            self.vx = PLAYER_SPEED
        if keys[pg.K_UP]:
            self.vy = -PLAYER_SPEED
        if keys[pg.K_DOWN]:
            self.vy = PLAYER_SPEED

    def update(self) -> None:
        """Update state each time round the game loop.
        Checks for user input, then handles movement and wall collisions.

        """
        self.get_keys()
        super().update()


class Enemy(Actor):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
