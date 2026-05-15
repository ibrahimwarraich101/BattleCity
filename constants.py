import pygame

# Screen Dimensions
TILE_SIZE = 26 # Slightly larger
GRID_SIZE = 26
GAME_AREA_WIDTH = GRID_SIZE * TILE_SIZE
HUD_WIDTH = 180 # Wider HUD for better info display
SCREEN_WIDTH = GAME_AREA_WIDTH + HUD_WIDTH
SCREEN_HEIGHT = GRID_SIZE * TILE_SIZE
FPS = 60 # Smoother frame rate
TICK_RATE_MS = 100 # Game logic tick rate
STAGE_SPLASH_TIME = 120 # 2 seconds at 60 FPS

# Colors - Premium Palette
COLOR_BG = (15, 15, 20)          # Dark navy background
COLOR_EMPTY = (20, 20, 25)       # Slightly lighter dark for empty tiles
COLOR_BRICK = (180, 60, 40)      # Vibrant brick red
COLOR_STEEL = (110, 120, 140)    # Cool steel blue-grey
COLOR_WATER = (30, 100, 200)     # Deep blue water
COLOR_FOREST = (40, 150, 60)     # Lush green forest
COLOR_EAGLE = (255, 200, 0)      # Golden eagle
COLOR_EAGLE_DEAD = (100, 100, 100)
COLOR_HUD = (30, 30, 40)         # Darker HUD
COLOR_UI_TEXT = (220, 220, 240)  # Off-white text
COLOR_BULLET = (255, 255, 100)   # Glowing yellow bullet

# Tank Colors
COLOR_PLAYER = (50, 200, 255)    # Neon Cyan
COLOR_ENEMY_BASIC = (180, 180, 180)
COLOR_ENEMY_FAST = (255, 100, 100) # Bright Red
COLOR_ENEMY_ARMOR = (150, 50, 200) # Purple
COLOR_BOSS_P1 = (255, 215, 0)    # Gold
COLOR_BOSS_P2 = (255, 100, 0)    # Orange
COLOR_BOSS_P3 = (255, 0, 50)     # Vibrant Red
COLOR_HP_BAR = (0, 255, 100)     # Green HP bar

# Tile Types
EMPTY = 0
BRICK = 1
STEEL = 2
WATER = 3
FOREST = 4
EAGLE = 5

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Spawn Points
PLAYER_SPAWN = (4, 24)
EAGLE_POS = (12, 24)
ENEMY_SPAWNS = [(0, 0), (12, 0), (24, 0)]

# Difficulty / Level Settings
MAX_WALL_DENSITY = 0.35  # 35% for better playability
TOTAL_TILES = GRID_SIZE * GRID_SIZE

# Tank Stats (Base delays in frames at 60 FPS)
PLAYER_SPEED = 6 
BULLET_SPEED = 1 # 1 tile per update
PLAYER_LIVES = 3
TOTAL_ENEMIES_PER_LEVEL = 20
MAX_ACTIVE_ENEMIES = 4

# Boss Stats
BOSS_HP_MAX = 12
BOSS_SPAWN = (17, 8)
BOSS_PLAYER_SPAWN = (8, 17)

# Boss Phases
BOSS_PHASES = {
    1: {'hp': (9, 12), 'speed': 8, 'fire_rate': 120, 'depth': 2},
    2: {'hp': (4, 8), 'speed': 6, 'fire_rate': 90, 'depth': 3},
    3: {'hp': (1, 3), 'speed': 4, 'fire_rate': 60, 'depth': 4}
}
