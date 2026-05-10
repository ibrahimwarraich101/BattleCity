import os
import sys
import pygame

os.environ['SDL_VIDEODRIVER'] = 'dummy'
sys.path.append(os.path.abspath('.'))

from main import Game
from constants import *

def test_boss_level_flow():
    print("Testing Boss Level Game Flow...")
    pygame.init()
    game = Game()
    
    # Simulate clicking 'B'
    print("Starting Boss Level...")
    game.start_splash('B')
    
    # Run through splash screen
    for _ in range(STAGE_SPLASH_TIME + 1):
        game.update()
    
    print(f"Game State after splash: {game.game_state}")
    if game.game_state != "BOSS_FIGHT":
        print(f"FAILED: Game state should be BOSS_FIGHT, got {game.game_state}")
        return False
    
    print(f"Boss spawned: {len(game.enemies)} enemy found.")
    if len(game.enemies) == 0 or game.enemies[0].tank_type != 'boss':
        print("FAILED: Boss Tank not found in enemies list!")
        return False

    # Simulate 10 seconds of gameplay (300 ticks)
    print("Simulating 10 seconds of Boss Fight...")
    try:
        for i in range(300):
            game.update()
            if i % 60 == 0:
                print(f"Tick {i}: Boss HP={game.enemies[0].hp}, Player Pos=({game.player.x}, {game.player.y})")
    except Exception as e:
        print(f"FAILED: Game crashed during simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("Boss Level Flow Test: PASSED")
    return True

if __name__ == "__main__":
    if test_boss_level_flow():
        sys.exit(0)
    else:
        sys.exit(1)
