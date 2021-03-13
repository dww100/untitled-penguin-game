from __future__ import annotations
import logging

from enum import Enum
from typing import Union, List, Tuple

import pygame as pg
from pygame.sprite import Sprite
from pygame.math import Vector2

from .settings import TILE_SIZE, GREEN, YELLOW, INFO_HEIGHT

LOGGER = logging.getLogger(__name__)


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
        self.pos = Vector2(x, y) * TILE_SIZE
        self.pos.y += INFO_HEIGHT
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        self.rect.y += INFO_HEIGHT


class Actor(Sprite):
    def __init__(
        self,
        game: "penguin_game.game.Game",
        x: int,
        y: int,
        additional_groups: Union[pg.sprite.Group, List[pg.sprite.Group], None] = None,
        no_movement_images: List[pg.Surface] = None,
        move_up_images: List[pg.Surface] = None,
        move_down_images: List[pg.Surface] = None,
        move_left_images: List[pg.Surface] = None,
        move_right_images: List[pg.Surface] = None,
        colour: Tuple[int, int, int] = YELLOW,
    ) -> None:
        """Base class for active Sprites that move and interact with their environment.

        Args:
            game: Game that this Sprite is associated with (provides access to timing, etc).
            x: Horizontal starting position in pixels.
            y: Vertical starting position in pixels.
            additional_groups: Sprite groups other than `game.all_sprites` to be associated with.
            colour: Colour tos use to fill place holder rect.
        """

        if additional_groups is None:
            self.groups = game.all_sprites
        else:
            if isinstance(additional_groups, list):
                self.groups = additional_groups + [game.all_sprites]
            else:
                self.groups = [additional_groups, game.all_sprites]

        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        if no_movement_images is not None:
            self.no_movement_images = no_movement_images
            self.image = self.no_movement_images[0]
        else:
            self.no_movement_images = [pg.Surface((TILE_SIZE, TILE_SIZE))]
            self.image = self.no_movement_images[0]
            self.image.fill(colour)

        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        self.rect.y += INFO_HEIGHT
        self.pos = Vector2(x, y) * TILE_SIZE
        self.pos.y += INFO_HEIGHT
        self.vel = Vector2(0, 0)

        self.original_pos = Vector2(self.pos)
        self.original_colour = colour

        self.stopped_by = [self.game.walls]
        self.killed_by = []
        self.killed = False

    def collide_and_stop(
        self, check_group: pg.sprite.Group, direction: Axis = Axis.X
    ) -> bool:
        """Handle collisions with a wall when moving along specified axis.

        Args:
            check_group: Sprite group to use in collision check.
            direction: Which axis are we checking for collisions along.
        """

        hits = pg.sprite.spritecollide(self, check_group, False)
        if hits:
            if direction == Axis.X:

                # X axis: +ve = right, -ve = left
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x

                self.blockedX = True

            else:
                # Y axis: +ve = down, -ve = up
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y

                self.blockedY = True

            return True

        else:

            return False

    def check_fatal_collisions(self) -> bool:
        """Check for collisions that could kill the Actor.

        Sets the `self.vel = (0, 0)` if so.

        Returns:
            Has the Actor collided with anything in the `self.killed_by`
            list of sprite groups.
        """

        if not self.killed_by:
            return False

        killed = False

        for killer in self.killed_by:
            killed_x = self.collide_and_stop(killer, Axis.X)
            killed_y = self.collide_and_stop(killer, Axis.Y)

            if killed_x or killed_y:
                self.vel = Vector2(0, 0)
                killed = True

        return killed

    def update(self) -> None:
        """Update state each time round the game loop.
        Handles movement and wall collisions.
        """
        self.blockedX = False
        self.blockedY = False

        # Scale movement to ensure reliable frame rate.
        self.pos += self.vel * self.game.dt

        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        self.killed = self.check_fatal_collisions()

        if not self.killed:
            for stopper in self.stopped_by:
                self.collide_and_stop(stopper, Axis.X)
                self.collide_and_stop(stopper, Axis.Y)
