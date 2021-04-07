TITLE = "Untitled Penguin Game"
# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (40, 40, 40)
LIGHT_GREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

BG_COLOR = DARK_GREY

# Target framerate
FPS = 60

TILE_SIZE = 64
# Dimensions of the game space in tiles
MAX_GRID_WIDTH = 20
MAX_GRID_HEIGHT = 20

# Dimensions of the game space in tiles
GRID_WIDTH = 17
GRID_HEIGHT = 12
# Dimensions of the game space in pixels
WIDTH = GRID_WIDTH * TILE_SIZE
HEIGHT = GRID_HEIGHT * TILE_SIZE

# Show grid lines to help check alignment
SHOW_GRID = False

# Height of info bar
INFO_HEIGHT = 32

# Player settings
START_LIVES = 2
PLAYER_SPEED = 0.5
DEATH_TIME = 60

# Block settings
BLOCK_SPEED = 1

# Game settings

# Time limit for level completion in seconds
TIME_LIMIT = 120
ENEMY_CLEARANCE_BONUS = 1000

# Enemy settings
ENEMY_SPEED = 0.3
ENEMY_IQ = 0.5  # zero to one
ENEMY_KILL_POINTS = 200

# Egg settings
EGG_BREAK_POINTS = 400
