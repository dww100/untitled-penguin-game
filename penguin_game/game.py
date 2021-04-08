import logging
from os import path
import sys
from enum import Enum
from typing import Optional, Tuple

import pygame as pg

from .level import Level
from .settings import (
    HEIGHT,
    WIDTH,
    INFO_HEIGHT,
    FPS,
    SHOW_GRID,
    TILE_SIZE,
    BG_COLOR,
    RED,
    LIGHT_GREY,
    WHITE,
    TITLE,
    TIME_LIMIT,
    START_LIVES,
    ENEMY_CLEARANCE_BONUS
)

from .entities import Wall

LOGGER = logging.getLogger(__name__)

image_dir = path.join(path.dirname(__file__), 'images')
sound_dir = path.join(path.dirname(__file__), 'sounds')
level_dir = path.join(path.dirname(__file__), 'levels')

TIMER = pg.USEREVENT + 1


class State(Enum):
    MENU = 1
    PLAY = 2
    GAME_OVER = 3


class InGameState(Enum):
    READY = 1
    RUNNING = 2
    COMPLETE = 3
    DIED = 4


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

        self.screen = pg.display.set_mode((WIDTH, INFO_HEIGHT + HEIGHT))
        self.clock = pg.time.Clock()

        LOGGER.debug(f"FPS limit: {FPS}\tInitial clock tick (ms): {self.clock.tick(FPS)}")

        self.dt = None

        self.all_sprites = None
        self.walls = None
        self.player = None
        self.blocks = None
        self.diamonds = None
        self.moving_blocks = None
        self.enemies = None
        self.stunned_enemies = None
        self.score = None
        self.lives = None
        self.start_ticks = None
        self.timer = None
        self.display_timer = None
        self.target_no_kills = None

        self.kill_bonus = None
        self.diamond_bonus = None

        self.state = State.MENU
        self.game_state = None

        self.sounds = {
            'swoosh': (pg.mixer.Sound(path.join(sound_dir, 'swoosh.wav')), 0),
            'death_self': (pg.mixer.Sound(path.join(sound_dir, 'down_arp.wav')), 1),
            'death_enemy': (pg.mixer.Sound(path.join(sound_dir, 'chords.wav')), 2),
            'electric': (pg.mixer.Sound(path.join(sound_dir, 'electric.wav')), 3),
        }

        self.sounds['death_self'][0].set_volume(0.2)
        self.sounds['death_enemy'][0].set_volume(0.6)
        self.sounds['electric'][0].set_volume(0.2)

    def setup_play(self, reset=False):
        """Initialize variables and setup for new game.
        """

        if reset:
            for sprite in self.all_sprites:
                sprite.kill()
        else:
            self.score = 0
            self.lives = START_LIVES
            self.game_state = InGameState.READY

        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.blocks = pg.sprite.Group()
        self.diamonds = pg.sprite.Group()
        self.moving_blocks = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.stunned_enemies = pg.sprite.Group()

        # level = Level(path.join(level_dir, '1.txt'))
        level = Level(path.join(level_dir, 'c64_level1.txt'))
        level.load_level(self)
        LOGGER.debug(f"No. enemies: {len(self.enemies)}, No. blocks: {len(self.blocks)}")

        self.make_boundary_wall(level.grid_height, level.grid_width)

        self.timer = TIME_LIMIT
        pg.time.set_timer(TIMER, 1000)

        self.target_no_kills = 5
        self.kill_bonus = None
        self.diamond_bonus = None

    def make_boundary_wall(self, height, width) -> None:
        """Create boundary for `Wall` Sprites around game grid.
        """
        for x in range(0, width):
            Wall(self, x, 0)
            Wall(self, x, height - 1)
        for y in range(1, height - 1):
            Wall(self, 0, y)
            Wall(self, width - 1, y)

    @staticmethod
    def quit() -> None:
        """Quit game and exit to system.
        """
        pg.quit()
        sys.exit()

    def run(self) -> None:
        pg.mixer.init()
        pg.mixer.music.load(path.join(sound_dir, 'theme.wav'))
        pg.mixer.music.set_volume(0.1)
        pg.mixer.music.play(-1, fade_ms=1000)
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
        self.draw_text("Space to push blocks", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 30)
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
                elif event.type == pg.KEYUP:
                    if event.key == pg.K_ESCAPE:
                        self.quit()
                    else:
                        self.state = State.PLAY
                        waiting = False

    def show_game_over_screen(self) -> None:
        """Show a game over screen and allow game to be restarted.
        """
        self.screen.fill(RED)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Game Over", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to return to menu", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("Esc to Quit", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4 + 30)
        pg.display.flip()

        # Wait for a key press.
        waiting = True
        while waiting:
            self.clock.tick(FPS)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.quit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.quit()
                    else:
                        waiting = False
                        self.state = State.MENU

    def run_game(self) -> None:
        """Execute main game loop
        """

        self.setup_play()
        pg.mixer.music.load(path.join(sound_dir, 'theme_full.wav'))
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play(-1, fade_ms=1000)

        while self.state == State.PLAY:

            # Using clock.tick each loop ensures framerate is limited to target FPS
            self.dt = self.clock.tick(FPS)

            self.events()

            if self.game_state == InGameState.READY:

                state_text = "READY!"

                if self.display_timer is None:
                    self.display_timer = 1

                elif self.display_timer == 0:
                    self.display_timer = None
                    self.game_state = InGameState.RUNNING

            elif self.game_state == InGameState.COMPLETE:

                state_text = "You survived!"

                if self.display_timer is None:
                    self.display_timer = 1

                elif self.display_timer == 0:
                    self.display_timer = None
                    self.setup_play(reset=True)
                    self.game_state = InGameState.READY

            else:

                self.update()

                if self.display_timer is None:
                    state_text = None
                elif self.display_timer == self.timer:
                    self.display_timer = None

                if self.player.death_timer == 0:
                    if self.lives == 0:
                        self.state = State.GAME_OVER
                    else:
                        self.setup_play(reset=True)
                        self.game_state = InGameState.READY

                if self.kill_bonus is None:

                    if self.no_kills() >= self.target_no_kills:

                        self.display_timer = self.timer - 2

                        half_time = TIME_LIMIT // 2
                        if self.timer >= half_time:
                            self.kill_bonus = (self.timer - half_time) // 10 * ENEMY_CLEARANCE_BONUS
                            state_text = f"Kill bonus: {self.kill_bonus}"
                        else:
                            self.kill_bonus = 0
                            state_text = f"Too slow - No kill bonus"

                if self.timer == 0:
                    self.game_state = InGameState.COMPLETE

            self.draw(state_text=state_text)

    def no_kills(self):
        return sum([e.deaths for e in self.enemies])

    def events(self) -> None:
        """Handle events - key presses etc.
        """

        for event in pg.event.get():
            if event.type == TIMER:
                if self.game_state == InGameState.RUNNING:
                    self.timer -= 1
                else:
                    self.display_timer -= 1

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
            pg.draw.line(self.screen, LIGHT_GREY, (x, INFO_HEIGHT), (x, HEIGHT))
        for y in range(INFO_HEIGHT, INFO_HEIGHT + HEIGHT, TILE_SIZE):
            pg.draw.line(self.screen, LIGHT_GREY, (0, y), (WIDTH, y))

    def draw_info(self) -> None:
        """Draw info line - lives and score
        """

        icon_size = INFO_HEIGHT - 6

        for i in range(self.lives):
            life_icon = pg.image.load(
                path.join(image_dir, f"pengo_left.png")
            ).convert_alpha()
            life_icon = pg.transform.scale(life_icon, (icon_size, icon_size))
            life_rect = life_icon.get_rect()
            life_rect.x = (INFO_HEIGHT - 2) * i
            life_rect.y = 3
            self.screen.blit(life_icon, life_rect)

        no_kills = self.no_kills()
        if no_kills >= self.target_no_kills:
            remaining_kills = 0
        else:
            remaining_kills = self.target_no_kills - no_kills

        self.draw_text("Kill target:", size=24, color=WHITE, x=WIDTH//2 - 250, y=6)
        self.draw_text(f"{remaining_kills}", size=24, color=WHITE, x=WIDTH//2 - 170, y=6)

        self.draw_text("Score:", size=24, color=WHITE, x=WIDTH//2 - 50, y=6)
        self.draw_text(f"{self.score}", size=24, color=WHITE, x=WIDTH//2 + 50, y=6)

        self.draw_text("Time:", size=24, color=WHITE, x=WIDTH//2 + 150, y=6)
        if self.timer > 0:
            time = self.timer
        else:
            time = 0
        self.draw_text(f"{time}", size=24, color=WHITE, x=WIDTH // 2 + 210, y=6)

    def draw(self, state_text: Optional[str] = None) -> None:
        """Draw new frame to the screen.
        """
        self.screen.fill(BG_COLOR)
        if SHOW_GRID:
            self.draw_grid()
        self.draw_info()
        self.all_sprites.draw(self.screen)
        if state_text is not None:
            self.draw_text(state_text, 75, WHITE, WIDTH // 2, HEIGHT // 2)
        pg.display.flip()
