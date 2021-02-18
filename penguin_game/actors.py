from __future__ import annotations

import pygame as pg
from pygame.math import Vector2

from .settings import TILE_SIZE, PLAYER_SPEED, BLOCK_SPEED, RED, BLUE
from .entities import Actor


def is_actor_neighbour_in_direction(actor1: Actor, actor2: Actor, direction: Vector2, tolerance: float = 10) -> bool:
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

        hits = pg.sprite.spritecollide(
            self, self.game.blocks, False, pg.sprite.collide_rect_ratio(1.1)
        )
        blocking = [
            hit for hit in hits if is_actor_neighbour_in_direction(self, hit, direction)
        ]
        if not blocking:
            self.vel = BLOCK_SPEED * direction
        else:
            # Logic for breaking
            pass

    def check_for_squish(self):
        pg.sprite.spritecollide(self, self.game.enemies, True)

    def update(self) -> None:
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

    def update(self) -> None:
        """Update state each time round the game loop.
        Checks for user input, then handles movement and wall collisions.

        """
        self.get_keys()
        super().update()


class Enemy(Actor):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, additional_groups=game.enemies, colour=BLUE)
