from .settings import MAX_GRID_HEIGHT, MAX_GRID_WIDTH
from .actors import Player, Block, Enemy

ELEMENTS = {
        ' ': None,
        '0': Block,
        '1': Player,
        '2': Enemy,
        '\n': None
}


class Level(object):

    def __init__(self, fname):
        self.fname = fname
        self.height, self.width = self.validate_input(self.fname)

    def load_sprites(self, game):
        def init_sprite(i, j, char):
            if ELEMENTS[char]:
                print(char, ELEMENTS[char])
                ELEMENTS[char](game, j, i)

        with open(self.fname, 'r') as f:
            for i, line in enumerate(f):
                for j, char in enumerate(line):
                    init_sprite(i, j, char)

    def validate_input(self, fname):
        n_lines = 0
        with open(fname, 'r') as f:
            for line in f:
                if n_lines == 0:
                    n_cols = len(line) 
                else:
                    assert len(line) == n_cols, "Level file has inconsistent width"
                n_lines += 1

                for c in line:
                    assert c in ELEMENTS.keys(), f"Level file: unrecognised token '{c}',\
                                                  must be one of {ELEMENTS}"

        n_cols -= 1 # ignore new line char
        assert n_lines < MAX_GRID_HEIGHT
        assert n_cols < MAX_GRID_WIDTH

        return n_lines, n_cols

if __name__ == "__main__":
    Level('levels/1.txt')

