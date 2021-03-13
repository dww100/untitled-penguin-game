from settings import MAX_GRID_HEIGHT, MAX_GRID_WIDTH

VALID_ELEMENTS = [' ', '0', '1', '2', '\n'] 


class Level(object):

    def __init__(self, fname):
        self.read_in_level_data(fname)

    def read_in_level_data(self, fname):
        height, width = self.validate_input(fname)
        print(height, width)

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
                    assert c in VALID_ELEMENTS, f"Level file: unrecognised token '{c}',\
                                                  must be one of {VALID_ELEMENTS}"

        n_cols -= 1 # ignore new line char
        assert n_lines < MAX_GRID_HEIGHT
        assert n_cols < MAX_GRID_WIDTH

        return n_lines, n_cols

if __name__ == "__main__":
    Level('levels/1.txt')

