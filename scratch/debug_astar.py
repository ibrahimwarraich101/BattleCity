import os, sys, pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
sys.path.insert(0, os.path.abspath('.'))
from constants import *
pygame.init()

from game_map import GameMap
from agents.armor_tank_agent import run_astar

gmap = GameMap(2)
# Test A* from each spawn to eagle
for sx, sy in ENEMY_SPAWNS:
    path = run_astar((sx, sy), EAGLE_POS, gmap.grid)
    print(f"Spawn ({sx},{sy}) to Eagle {EAGLE_POS}: path length = {len(path) if path else 0}, first steps = {path[:3] if path else 'NONE'}")
