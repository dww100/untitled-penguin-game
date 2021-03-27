from __future__ import annotations
import logging

from os import path
from typing import Union
from .utils import play_sound
import numpy as np

import pygame as pg
from pygame.math import Vector2

from .settings import (
    TILE_SIZE,
    INFO_HEIGHT,
    PLAYER_SPEED,
    DEATH_TIME,
    BLOCK_SPEED,
    ENEMY_SPEED,
    ENEMY_IQ,
    ENEMY_KILL_POINTS,
    RED,
    BLUE,
    YELLOW,
    WHITE,
)
from .entities import Actor, Wall, ScoreMarker

image_dir = path.join(path.dirname(__file__), "images")

LOGGER = logging.getLogger(__name__)


def is_actor_neighbour_in_direction(
    actor1: Union[Actor, Wall],
    actor2: Union[Actor, Wall],
    direction: Vector2,
    tolerance: float = 12,
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
    return difference.length() <= tolerance


class Block(Actor):
    def __init__(
        self, game: "penguin_game.game.Game", x: int, y: int, diamond=False
    ) -> None:
        """Block Sprite.

        Args:
            game: Game that this Sprite is associated with (provides access to timing, etc).
            x: Horizontal starting position in pixels.
            y: Vertical starting position in pixels.
            diamond: Is this a diamond?
        """

        if diamond:
            static_images = [
                pg.image.load(
                    path.join(image_dir, "block_yellow64x64.png")
                ).convert_alpha()
            ]
            self.diamond = True
        else:
            static_images = [
                pg.image.load(path.join(image_dir, "block64x64.png")).convert_alpha()
            ]
            self.diamond = False

        super().__init__(
            game,
            x,
            y,
            additional_groups=game.blocks,
            move_up_images=static_images,
            move_down_images=static_images,
            move_left_images=static_images,
            move_right_images=static_images,
        )

        self.stopped_by.append(game.blocks)

    def respond_to_push(self, direction: Vector2):
        """Respond to a push by moving in a direction if free to do so or breaking.

        Args:
            direction: direction of attempted push - determines movement direction.
        """

        play_sound(self.game.sounds["swoosh"])

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
            self.game.blocks.remove(self)
            self.game.moving_blocks.add(self)

        elif not self.diamond:
            self.kill()

    def update(self) -> None:
        """Update state each time round the game loop.
        Handles movement and collisions. If moving can squish enemies.
        """

        if self.vel.magnitude() == 0:

            if self in self.game.moving_blocks:
                self.game.moving_blocks.remove(self)
                self.game.blocks.add(self)

        super().update()


class Diamond(Block):
    def __init__(
        self, game: "penguin_game.game.Game", x: int, y: int, diamond=False
    ) -> None:
        """Block Sprite.

        Args:
            game: Game that this Sprite is associated with (provides access to timing, etc).
            x: Horizontal starting position in pixels.
            y: Vertical starting position in pixels.
            diamond: Is this a diamond?
        """
        super().__init__(
            game,
            x,
            y,
            diamond=True,
        )

        self.groups.append(game.diamonds)


class Player(Actor):
    def __init__(self, game: "penguin_game.game.Game", x: int, y: int,) -> None:
        """Player Sprite.

        Args:
            game: Game that this Sprite is associated with (provides access to timing, etc).
            x: Horizontal starting position in pixels.
            y: Vertical starting position in pixels.
        """

        move_up_images = []
        for frame_no in range(1, 3):
            move_up_images.append(pg.image.load(
                    path.join(image_dir, f"pengo_back{frame_no}.png")
                ).convert_alpha())
        move_down_images = []
        for frame_no in range(1, 3):
            move_down_images.append(pg.image.load(
                    path.join(image_dir, f"pengo_front{frame_no}.png")
                ).convert_alpha())
        move_left_images = [pg.image.load(
                    path.join(image_dir, f"pengo_left.png")
                ).convert_alpha()]
        move_right_images = [pg.image.load(
                    path.join(image_dir, f"pengo_right.png")
                ).convert_alpha()]

        super().__init__(
            game,
            x,
            y,
            initial_direction=Vector2(0, 1),
            additional_groups=None,
            move_up_images=move_up_images,
            move_down_images=move_down_images,
            move_left_images=move_left_images,
            move_right_images=move_right_images,
        )
        self.stopped_by.append(game.blocks)
        self.killed_by.append(game.enemies)
        self.vel = Vector2(0, 0)
        self.last_pos = Vector2(x, y)
        self.frozen = False
        self.death_timer = None

        self.death_images = []
        for frame_no in range(1, 4):
            self.death_images.append(pg.image.load(
                    path.join(image_dir, f"pengo_dead{frame_no}.png")
                ).convert_alpha())

    def get_keys(self) -> None:
        """Handle keyboard input.
        """

        keys = pg.key.get_pressed()

        self.vel = Vector2(0, 0)
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

        self.last_pos = Vector2(self.pos)

    def push(self) -> None:
        """Look for block to push and if one is close in direction faced - push it.
        """

        hits = pg.sprite.spritecollide(
            self, self.game.blocks, False, pg.sprite.collide_circle_ratio(1.2)
        )
        hits = [h for h in hits if is_actor_neighbour_in_direction(
            self, h, self.facing
        )]

        if hits:

            hits[0].respond_to_push(self.facing)

        hits = pg.sprite.spritecollide(
            self, self.game.walls, False, pg.sprite.collide_circle_ratio(0.75)
        )

        if [h for h in hits if is_actor_neighbour_in_direction(
            self, h, self.facing
        )]:
            play_sound(self.game.sounds["electric"])

    def death_update(self) -> None:
        """Update the death times and image shown after player dies.
        """
        self.death_timer -= 1

        gap = DEATH_TIME // 3
        # TODO: Replace with a good animation
        frame = int(self.death_timer / gap) - 1
        self.image = self.death_images[frame]

    def update(self) -> None:
        """Update state each time round the game loop.
        Checks for user input, then handles movement and wall collisions.
        """

        change_direction = False

        # Player could be frozen on death or a restart - ignore user input
        if not self.frozen:
            self.get_keys()

        super().update()

        # Enact post death animation while timer is set
        if self.death_timer is not None:
            self.death_update()

        # self.killed set during super.update()
        elif self.killed:
            play_sound(self.game.sounds["death_self"])
            self.game.lives -= 1
            self.frozen = True
            self.death_timer = DEATH_TIME
        else:
            self.update_animation(direction_change=change_direction)


class Enemy(Actor):
    def __init__(
        self, game, x, y, initial_direction: "pygame.math.Vector2" = Vector2(0, 1), point_value=ENEMY_KILL_POINTS,
    ):

        move_up_images = [
            pg.image.load(path.join(image_dir, "chick_back.png")).convert_alpha()
        ]
        move_down_images = [
            pg.image.load(path.join(image_dir, "chick_front.png")).convert_alpha()
        ]
        move_left_images = [
            pg.image.load(path.join(image_dir, "chick_left.png")).convert_alpha()
        ]
        move_right_images = [
            pg.image.load(path.join(image_dir, "chick_right.png")).convert_alpha()
        ]

        super().__init__(
            game,
            x,
            y,
            initial_direction=initial_direction,
            additional_groups=game.enemies,
            move_up_images=move_up_images,
            move_down_images=move_down_images,
            move_left_images=move_left_images,
            move_right_images=move_right_images,
        )

        self.stopped_by.append(game.blocks)
        self.killed_by.append(game.moving_blocks)
        self.vel = self.facing * ENEMY_SPEED
        self.hunt = False
        self.point_value = point_value

    def choose_new_direction(self, init_facing):
        turn_options = [self.facing * -1]
        if self.facing.x == 0:
            turn_options += [Vector2(1, 0), Vector2(-1, 0)]
        else:
            turn_options += [Vector2(0, 1), Vector2(0, -1)]
        random_turn = turn_options[np.random.randint(3)]

        # find direction to player
        x = self.pos.x - self.game.player.pos.x
        y = self.pos.y - self.game.player.pos.y
        if abs(x) > abs(y):
            if x > 0:
                chase = Vector2(-1, 0)
            else:
                chase = Vector2(1, 0)
        else:
            if y > 0:
                chase = Vector2(0, -1)
            else:
                chase = Vector2(0, 1)

        if chase == init_facing:
            # Too dumb to know how to chase
            # TODO: add path finding here
            return random_turn

        if np.random.random() < ENEMY_IQ or self.hunt:
            return chase
        else:
            return random_turn

    def update(self) -> None:

        init_facing = self.facing

        super().update()

        # Being stopped means the enemy has collided with something
        # -  Therefore need to change direction
        if not self.vel.magnitude():
            self.facing = self.choose_new_direction(init_facing)
            self.vel = self.facing * ENEMY_SPEED

            self.update_animation(direction_change=True)

        else:
            self.update_animation()

        if self.killed:
            play_sound(self.game.sounds["death_enemy"])
            self.game.score += self.point_value
            score_marker = ScoreMarker(self.point_value, x=self.rect.x, y=self.rect.y)
            self.game.all_sprites.add(score_marker)
            self.kill()
