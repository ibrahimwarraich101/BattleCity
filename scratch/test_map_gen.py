import os
import sys
import pygame

# Mock pygame display to run headless
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Add project root to path
sys.path.append(os.path.abspath('.'))

from game_map import GameMap
from constants import *

def test_map_generation():
    print("Starting Map Generation Stress Test...")
    for level in [1, 2, 'B']:
        print(f"Testing Level {level} generation...")
        for i in range(50): # Test 50 random maps per level
            try:
                gmap = GameMap(level)
                if level != 'B':
                    # Check reachability (using the strict check I implemented)
                    for sx, sy in ENEMY_SPAWNS:
                        if not gmap._can_reach(sx, sy, EAGLE_POS[0], EAGLE_POS[1]):
                            print(f"FAILED: Reachability check failed on Level {level}, iteration {i}")
                            return False
                else:
                    # Check arena bounds
                    if gmap.grid[7][7] != EMPTY or gmap.grid[18][18] != EMPTY:
                        print(f"FAILED: Boss Arena bounds invalid on iteration {i}")
                        return False
            except Exception as e:
                print(f"FAILED: Exception during generation on Level {level}, iteration {i}: {e}")
                return False
        print(f"Level {level} passed 50/50.")
    print("Map Generation Stress Test: PASSED")
    return True

if __name__ == "__main__":
    pygame.init()
    if test_map_generation():
        sys.exit(0)
    else:
        sys.exit(1)
