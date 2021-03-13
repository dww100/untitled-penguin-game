from .settings import MAX_GRID_HEIGHT, MAX_GRID_WIDTH
from .actors import Player, Block, Enemy

ELEMENTS = {
        '.': None,
        '0': Block,
        '1': Player,
        '2': Enemy,
        '\n': None
}


class Level(object):

    def __init__(self, filename, validate_only=False):
        self.filename = filename
        self.element_grid = None
        self.element_height = None
        self.element_width = None

        # height, width = self.validate_input(self.fname)
        # self.height = height + 2
        # self.width = width + 2

    @property
    def grid_width(self):
        if self.element_width is not None:
            return self.element_width + 2

        return None

    @property
    def grid_height(self):
        if self.element_height is not None:
            return self.element_height + 2

        return None

    def load_level(self, game=None):
        self.parse_input_file()
        if game is not None:
            self._load_sprites(game)

    def _load_sprites(self, game):

        def init_sprite(i, j, char):
            obj = ELEMENTS[char]
            if obj:
                if obj is Player:
                    game.player = obj(game, j, i)
                else:
                    obj(game, j, i)

        for row, line in enumerate(self.element_grid):
            for column, char in enumerate(line):
                init_sprite(row + 1, column + 1, char)

    def parse_input_file(self):

        element_grid = []

        n_lines = 0
        with open(self.filename, 'r') as f:
            for line in f:
                stripped_line = line.strip()
                if n_lines == 0:
                    n_cols = len(stripped_line)
                else:
                    assert len(stripped_line) == n_cols, "Level file has inconsistent width"
                n_lines += 1

                unrecognised = [c for c in stripped_line if c not in ELEMENTS]
                if unrecognised:
                    raise RuntimeError(f"Invalid level file: Unrecognised tokens "
                                       f"{unrecognised} on line {n_lines}, must be "
                                       f"one of {ELEMENTS.keys()}")
                element_grid.append(stripped_line)

        # Check valid grid size - 3 characters used per row/column for walls
        assert n_lines <= MAX_GRID_HEIGHT - 2
        assert n_cols <= MAX_GRID_WIDTH - 2

        self.element_grid = element_grid
        self.element_height, self.element_width = n_lines, n_cols


if __name__ == "__main__":
    test_level = Level('levels/1.txt')
    test_level.load_level()
    print(test_level.element_grid)

