import pygame

# Screen Dimensions
TILE_SIZE = 24
GRID_SIZE = 26
GAME_AREA_WIDTH = GRID_SIZE * TILE_SIZE
HUD_WIDTH = 120
SCREEN_WIDTH = GAME_AREA_WIDTH + HUD_WIDTH
SCREEN_HEIGHT = GRID_SIZE * TILE_SIZE
FPS = 30
MENU_FONT_SIZE = 48
STATS_FONT_SIZE = 14
STAGE_SPLASH_TIME = 60 # 2 seconds

# Colors
COLOR_EMPTY = (26, 26, 26)      # #1a1a1a
COLOR_BRICK = (139, 37, 0)      # #8B2500
COLOR_STEEL = (170, 170, 170)    # #AAAAAA
COLOR_WATER = (26, 107, 160)     # #1a6ba0
COLOR_FOREST = (45, 90, 27)      # #2d5a1b
COLOR_EAGLE = (255, 215, 0)      # Yellow/Gold
COLOR_HUD = (50, 50, 50)
COLOR_TEXT = (255, 255, 255)

# Tank Colors
COLOR_PLAYER = (0, 255, 0)
COLOR_ENEMY_BASIC = (150, 150, 150)
COLOR_ENEMY_FAST = (255, 255, 255)
COLOR_ENEMY_ARMOR = (139, 0, 0)
COLOR_BOSS_P1 = (255, 215, 0) # Gold
COLOR_BOSS_P2 = (255, 140, 0) # Orange
COLOR_BOSS_P3 = (255, 0, 0)   # Red
COLOR_HP_BAR = (200, 0, 0)
COLOR_ENEMY_BOSS = (255, 215, 0)

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
MAX_WALL_DENSITY = 0.40  # 40%
TOTAL_TILES = GRID_SIZE * GRID_SIZE

# Tank Stats
PLAYER_SPEED = 8 # Matches basic tank (Very slow)
BULLET_SPEED = 1 
PLAYER_LIVES = 10
TOTAL_ENEMIES_PER_LEVEL = 20
MAX_ACTIVE_ENEMIES = 3

# Boss Stats
BOSS_HP_MAX = 10
BOSS_SPAWN = (17, 8)
BOSS_PLAYER_SPAWN = (8, 17)

# Boss Phases
BOSS_PHASES = {
    1: {'hp': (7, 10), 'speed': 6, 'fire_rate': 150, 'depth': 2},
    2: {'hp': (3, 6), 'speed': 5, 'fire_rate': 120, 'depth': 3},
    3: {'hp': (1, 2), 'speed': 4, 'fire_rate': 90, 'depth': 4}
}
