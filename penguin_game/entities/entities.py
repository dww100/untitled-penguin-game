from __future__ import annotations
import logging

from enum import Enum
from typing import Optional, Union, List, Tuple

import pygame as pg
from pygame.sprite import Sprite
from pygame.math import Vector2

from penguin_game.settings import TILE_SIZE, GREEN, WHITE, BLACK, INFO_HEIGHT
from penguin_game.utils import play_sound

LOGGER = logging.getLogger(__name__)

ENTITIES = {}


class Axis(Enum):
    X = 0
    Y = 1


class BaseEntity(Sprite):
    id = None
    text_name = ''

    def __init_subclass__(cls, *args, **kwargs):
        """
        Catch any new scoring functions (all entities must inherit
        from this base class) and add them to the dict of entities.
        """
        super().__init_subclass__(**kwargs)

        if cls.id is not None:
            # Register new entity
            ENTITIES[cls.id] = cls


class Wall(BaseEntity):
    id = '0'
    text_name = 'Wall'

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

    def respond_to_push(self, direction):
        play_sound(self.game.sounds['electric'])


class Actor(BaseEntity):
    def __init__(
        self,
        game: "penguin_game.game.Game",
        x: int,
        y: int,
        initial_direction: "pygame.math.Vector2" = Vector2(0, 1),
        additional_groups: Union[pg.sprite.Group, List[pg.sprite.Group], None] = None,
        move_up_images: List[pg.Surface] = None,
        move_down_images: List[pg.Surface] = None,
        move_left_images: List[pg.Surface] = None,
        move_right_images: List[pg.Surface] = None,
        colour: Optional[Tuple[int, int, int]] = None,
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
            self.groups = [game.all_sprites]
        else:
            if isinstance(additional_groups, list):
                self.groups = additional_groups + [game.all_sprites]
            else:
                self.groups = [additional_groups, game.all_sprites]

        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.facing = initial_direction

        self.animation_frame = 0
        self.last_update = 0
        self.update_freq = 5

        if colour is not None:
            images = [pg.Surface((TILE_SIZE, TILE_SIZE))]

            self.move_up_images = images
            self.move_down_images = images
            self.move_left_images = images
            self.move_right_images = images
            self.image = images[0]
            self.image.fill(colour)

        else:

            self.move_up_images = move_up_images
            self.move_down_images = move_down_images
            self.move_left_images = move_left_images
            self.move_right_images = move_right_images
            self.image = move_down_images[0]

        self.rect = self.image.get_rect()
        self.pos = Vector2(0, 0)
        self.set_position(x, y)

        self.snap_to_grid = True

        self.vel = Vector2(0, 0)

        self.original_pos = Vector2(self.pos)
        self.original_colour = colour

        self.stopped_by = [self.game.walls]
        self.killed_by = []
        self.killed = False

    def set_position(self, x, y):
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        self.rect.y += INFO_HEIGHT
        self.pos = Vector2(x, y) * TILE_SIZE
        self.pos.y += INFO_HEIGHT

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

            else:
                # Y axis: +ve = down, -ve = up
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y

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

    def update_animation(self, direction_change=False):

        if self.vel != Vector2(0, 0):
            if self.facing == Vector2(0, 1):
                images = self.move_down_images
            elif self.facing == Vector2(0, -1):
                images = self.move_up_images
            elif self.facing == Vector2(1, 0):
                images = self.move_right_images
            else:
                images = self.move_left_images

            if self.image not in images:
                self.animation_frame = 0
                self.last_update = 0
            elif self.last_update % self.update_freq:
                self.animation_frame = (self.animation_frame + 1) % len(images)
                self.last_update = 0
            else:
                self.last_update += 1

            self.image = images[self.animation_frame]

    def update(self) -> None:
        """Update state each time round the game loop.
        Handles movement and wall collisions.
        """
        # Scale movement to ensure reliable frame rate.
        self.pos += self.vel * self.game.dt

        if self.snap_to_grid:
            if self.vel.x == 0:
                delta = self.pos.x % TILE_SIZE
                self.pos.x -= delta
                if delta > TILE_SIZE / 2:
                    self.pos.x += TILE_SIZE

            if self.vel.y == 0:
                delta = (self.pos.y - INFO_HEIGHT) % TILE_SIZE
                self.pos.y -= delta
                if delta > TILE_SIZE / 2:
                    self.pos.y += TILE_SIZE

        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        self.killed = self.check_fatal_collisions()

        if not self.killed:
            for stopper in self.stopped_by:
                self.collide_and_stop(stopper, Axis.X)
                self.collide_and_stop(stopper, Axis.Y)


class ScoreMarker(pg.sprite.Sprite):
    def __init__(self, score, x, y, color=WHITE, start_size=24, steps=5):

        # Call the parent class (Sprite) constructor
        pg.sprite.Sprite.__init__(self)
        self.text_size = start_size
        self.color = color
        self.score = score

        self.x = x
        self.y = y

        self.image = None
        self.rect = None
        self._blit_score()

        self.current_step = 0
        self.steps = steps
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 200

    def _blit_score(self):
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.set_colorkey(BLACK)
        font = pg.font.Font(pg.font.get_default_font(), int(self.text_size))
        text_surface = font.render(str(self.score), 1, self.color)
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        self.image.blit(text_surface, [TILE_SIZE/2 - text_width/2, TILE_SIZE/2 - text_height/2])
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self) -> None:

        now = pg.time.get_ticks()

        if now - self.last_update > self.frame_rate:

            if self.current_step == self.steps:
                self.kill()
            else:
                self.last_update = now
                self.current_step += 1
                self.text_size = self.text_size / 2
                self._blit_score()
