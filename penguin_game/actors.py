from __future__ import annotations
import logging

from typing import Union

import pygame as pg
from pygame.math import Vector2

from .settings import TILE_SIZE, PLAYER_SPEED, DEATH_TIME, BLOCK_SPEED, RED, BLUE, YELLOW, WHITE
from .entities import Actor, Wall

LOGGER = logging.getLogger(__name__)


def is_actor_neighbour_in_direction(
    actor1: Union[Actor, Wall],
    actor2: Union[Actor, Wall],
    direction: Vector2,
    tolerance: float = 10,
) -> bool:
    """Check if actor1 is a direct neighbour of actor2 in direction

    Args:
        actor1: Actor which is origin of comparison.
        actor2: Actor being considered as potential neighbour.
        direction: Direction of interest.
        tolerance: Allowable distance tolerance.

    Returns:
        bool: Is actor2 a neighbour of actor1 in desired direction.
    """

    actor_direction = actor2.pos - actor1.pos
    difference = actor_direction - direction * TILE_SIZE
    if difference.length() <= tolerance:
        return True
    else:
        return False


class Block(Actor):
    def __init__(self, game: "penguin_game.game.Game", x: int, y: int,) -> None:
        """Block Sprite.

        Args:
            game: Game that this Sprite is associated with (provides access to timing, etc).
            x: Horizontal starting position in pixels.
            y: Vertical starting position in pixels.
        """
        super().__init__(game, x, y, additional_groups=game.blocks)
        self.image.fill(RED)

    def respond_to_push(self, direction: Vector2):
        """Respond to a push by moving in a direction if free to do so or breaking.

        Args:
            direction: direction of attempted push - determines movement direction.
        """
        self.game.sounds['swoosh'].play()

        hits = pg.sprite.spritecollide(
            self, self.game.blocks, False, pg.sprite.collide_rect_ratio(1.1)
        )
        hits += pg.sprite.spritecollide(
            self, self.game.walls, False, pg.sprite.collide_rect_ratio(1.1)
        )
        blocking = [
            hit for hit in hits if is_actor_neighbour_in_direction(self, hit, direction)
        ]

        if not blocking:
            self.vel = BLOCK_SPEED * direction
        else:
            self.kill()

    def check_for_squish(self):
        """If Block collides with an enemy the enemy should die.
        """
        pg.sprite.spritecollide(self, self.game.enemies, True)

    def update(self) -> None:
        """Update state each time round the game loop.
        Handles movement and collisions. If moving can squish enemies.
        """
        if self.vel != Vector2(0, 0):
            self.check_for_squish()
        super().update()


class Player(Actor):
    def __init__(self, game: "penguin_game.game.Game", x: int, y: int,) -> None:
        """Player Sprite.

        Args:
            game: Game that this Sprite is associated with (provides access to timing, etc).
            x: Horizontal starting position in pixels.
            y: Vertical starting position in pixels.
        """
        super().__init__(game, x, y, additional_groups=None)
        self.stopped_by.append(game.blocks)
        self.killed_by.append(game.enemies)
        # Start facing left
        self.facing = Vector2(-1, 0)
        self.lives = 2
        self.frozen = False
        self.death_timer = None

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
            self.push()

    def push(self) -> None:
        """Look for block to push and if one is close in direction faced - push it.
        """

        hits = pg.sprite.spritecollide(
            self, self.game.blocks, False, pg.sprite.collide_circle_ratio(0.75)
        )

        if len(hits) == 1 and is_actor_neighbour_in_direction(
            self, hits[0], self.facing
        ):

            hits[0].respond_to_push(self.facing)

    def reset(self):
        self.image.fill(self.original_colour)
        self.pos = self.original_pos
        self.death_timer = None
        self.frozen = False

    def death_update(self):
        self.death_timer -= 1
        if self.death_timer % 2:
            self.image.fill(WHITE)
        else:
            self.image.fill(YELLOW)

    def update(self) -> None:
        """Update state each time round the game loop.
        Checks for user input, then handles movement and wall collisions.

        """

        if not self.frozen:
            self.get_keys()

        if self.death_timer is not None:
            self.death_update()

        super().update()

        if self.killed:
            self.lives -= 1
            self.frozen = True
            self.death_timer = DEATH_TIME


class Enemy(Actor):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, additional_groups=game.enemies, colour=BLUE)

