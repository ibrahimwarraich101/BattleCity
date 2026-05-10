import os
import sys
import pygame

os.environ['SDL_VIDEODRIVER'] = 'dummy'
sys.path.append(os.path.abspath('.'))

from game_map import GameMap
from constants import *

def test_map_generation():
    print("Starting Short Map Generation Test...")
    for level in [1, 2, 'B']:
        print(f"Testing Level {level}...")
        for i in range(10):
            gmap = GameMap(level)
            if level != 'B':
                for sx, sy in ENEMY_SPAWNS:
                    if not gmap._can_reach(sx, sy, EAGLE_POS[0], EAGLE_POS[1]):
                        print(f"FAIL: iteration {i}")
                        return False
            print(f".", end="", flush=True)
        print(f" Level {level} OK")
    print("ALL PASSED")
    return True

if __name__ == "__main__":
    pygame.init()
    test_map_generation()
