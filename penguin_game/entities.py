from __future__ import annotations

from enum import Enum
from typing import Union, List

import pygame as pg
from pygame.sprite import Sprite
from pygame.math import Vector2

from .settings import TILE_SIZE, GREEN, YELLOW


class Axis(Enum):
    X = 0
    Y = 1


class Wall(Sprite):
    def __init__(self, game: "penguin_game.game.Game", x: int, y: int) -> None:
        """Sprite class to describe bounding wall elements.

        Args:
            game: Game that this Sprite is associated with (provides access to timing, etc).
            x: Horizontal starting position in pixels.
            y: Vertical starting position in pixels.
        """
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.pos = Vector2(x, y)
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE


class Actor(Sprite):
    def __init__(
        self,
        game: "penguin_game.game.Game",
        x: int,
        y: int,
        additional_groups: Union[pg.sprite.Group, List[pg.sprite.Group], None] = None,
    ) -> None:
        """Base class for active Sprites that move and interact with their environment.

        Args:
            game: Game that this Sprite is associated with (provides access to timing, etc).
            x: Horizontal starting position in pixels.
            y: Vertical starting position in pixels.
            additional_groups: Sprite groups other than `game.all_sprites` to be associated with.
        """

        if additional_groups is None:
            self.groups = game.all_sprites
        else:
            if isinstance(additional_groups, list):
                self.groups = additional_groups + [game.all_sprites]
            else:
                self.groups = additional_groups, game.all_sprites

        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.x = y * TILE_SIZE
        self.pos = Vector2(x, y) * TILE_SIZE
        self.vel = Vector2(0, 0)

        self.stopped_by = [self.game.walls]

    def collide_and_stop(self, check_group: pg.sprite.Group, direction: Axis = Axis.X) -> bool:
        """Handle collisions with a wall when moving along specified axis.

        Args:
            check_group: Sprite group to use in collision check.
            direction: Which axis are we checking for collisions along.
        """

        hits = pg.sprite.spritecollide(self, check_group, False)
        if hits:
            if direction == Axis.X:

                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x

            else:

                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y

            return True

        else:

            return False

    def update(self) -> None:
        """Update state each time round the game loop.
        Handles movement and wall collisions.
        """

        # Scale movement to ensure reliable frame rate.
        self.pos += self.vel * self.game.dt

        self.rect.x = self.pos.x
        for stopper in self.stopped_by:
            self.collide_and_stop(stopper, Axis.X)

        self.rect.y = self.pos.y
        for stopper in self.stopped_by:
            self.collide_and_stop(stopper, Axis.Y)

    def die(self):
        self.remove(self.groups)
