import os
import sys
import pygame

os.environ['SDL_VIDEODRIVER'] = 'dummy'
sys.path.append(os.path.abspath('.'))

from main import Game
from constants import *

def test_boss_movement():
    print("Testing Boss Movement...")
    pygame.init()
    game = Game()
    game.start_splash('B')
    
    # Run through splash screen
    for _ in range(STAGE_SPLASH_TIME + 1):
        game.update()
    
    initial_dist = abs(game.enemies[0].x - game.player.x) + abs(game.enemies[0].y - game.player.y)
    print(f"Initial Distance: {initial_dist}")
    
    # Simulate 5 seconds (150 ticks)
    for i in range(150):
        game.update()
    
    final_dist = abs(game.enemies[0].x - game.player.x) + abs(game.enemies[0].y - game.player.y)
    print(f"Final Distance: {final_dist}")
    
    if final_dist < initial_dist:
        print("SUCCESS: Boss moved towards player.")
        return True
    else:
        print("FAILED: Boss did not move towards player.")
        return False

if __name__ == "__main__":
    if test_boss_movement():
        sys.exit(0)
    else:
        sys.exit(1)
