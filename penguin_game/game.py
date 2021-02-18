import logging
import sys
from enum import Enum
from typing import Optional, Tuple

import pygame as pg

from .settings import (
    HEIGHT,
    WIDTH,
    GRID_HEIGHT,
    GRID_WIDTH,
    FPS,
    TILE_SIZE,
    BG_COLOR,
    LIGHT_GREY,
    WHITE,
    TITLE,
)
from .actors import Player, Block, Enemy
from .entities import Wall

LOGGER = logging.getLogger(__name__)


class State(Enum):
    MENU = 1
    PLAY = 2
    GAME_OVER = 3


class Game:
    """Main game running object

    Attributes:
        screen (pg.Surface): Pygame object for representing images - here the main game space.
        clock (pg.time.Clock): Clock to track game time and help regulate framerate.
        dt (Optional[int]): Size of time increment (framerate in ms/ 1000) [None outside game loop].
        all_sprites (Optional[pg.sprite.Group]): Group of all game sprite [None outside game loop].
        walls (Optional[pg.sprite.Group]): Group of sprites defining edge of game area [None outside game loop].
        state (State): What state is the game in - MENU, PLAY or GAME_OVER.
    """

    def __init__(self):

        pg.init()

        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        LOGGER.debug(self.clock.tick(FPS))
        LOGGER.debug(FPS)
        self.dt = None

        self.all_sprites = None
        self.walls = None
        self.player = None
        self.blocks = None
        self.enemies = None

        self.state = State.MENU

    def setup_play(self):
        """Initialize variables and setup for new game.
        """
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.blocks = pg.sprite.Group()
        Block(self, 5, 6)
        Block(self, 5, 7)
        self.enemies = pg.sprite.Group()
        Enemy(self, 7, 7)
        self.player = Player(self, 5, 5)
        self.make_boundary_wall()

    def make_boundary_wall(self) -> None:
        """Create boundary for `Wall` Sprites around game grid.
        """
        for x in range(0, GRID_WIDTH):
            Wall(self, x, 0)
            Wall(self, x, GRID_HEIGHT - 1)
        for y in range(1, GRID_HEIGHT - 1):
            Wall(self, 0, y)
            Wall(self, GRID_WIDTH - 1, y)

    @staticmethod
    def quit() -> None:
        """Quit game and exit to system.
        """
        pg.quit()
        sys.exit()

    def run(self) -> None:
        while True:
            if self.state == State.MENU:
                self.show_menu()
            if self.state == State.GAME_OVER:
                self.show_game_over_screen()
            if self.state == State.PLAY:
                self.run_game()

    def draw_text(
        self, text: str, size: int, color: Tuple[int, int, int], x: int, y: int
    ) -> None:
        """Draw some text to the pygame screen.

        Args:
            text: Text to put on the screen
            size: Text size - height in pixels.
            color: Tuple containing the RGB values for the colour to use when rendering text.
            x: X coordinate of the middle top of the text.
            y: Y coordinate of the middle top of the text.
        """
        # TODO: Select and use a better font
        font = pg.font.Font(pg.font.get_default_font(), size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def show_menu(self) -> None:
        """Display start screen/menu.
        """
        self.screen.fill(BG_COLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows to move", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("Esc to Quit", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4 + 30)
        pg.display.flip()

        # Wait for a key press.
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False
                    self.state = State.PLAY

    def show_game_over_screen(self) -> None:
        """Show a game over screen and allow game to be restarted.
        """
        pass

    def run_game(self) -> None:
        """Execute main game loop
        """

        self.setup_play()

        while self.state == State.PLAY:
            # Using clock.tick each loop ensures framerate is limited to target FPS
            self.dt = self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self) -> None:
        """Handle events - key presses etc.
        """

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def update(self) -> None:
        """Update Sprites each time through game loop.
        """
        self.all_sprites.update()

    def draw_grid(self) -> None:
        """Draw a grid to indicate tile boundaries.
        Note: for testing only.
        """
        for x in range(0, WIDTH, TILE_SIZE):
            pg.draw.line(self.screen, LIGHT_GREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILE_SIZE):
            pg.draw.line(self.screen, LIGHT_GREY, (0, y), (WIDTH, y))

    def draw(self) -> None:
        """Draw new frame to the screen.
        """
        self.screen.fill(BG_COLOR)
        self.draw_grid()
        self.all_sprites.draw(self.screen)
        pg.display.flip()
