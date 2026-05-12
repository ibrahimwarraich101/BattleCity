import os, sys, pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
sys.path.insert(0, os.path.abspath('.'))

from main import Game
from constants import *

def test_boss_shoots():
    print("=== Test: Boss fires at player ===")
    pygame.init()
    game = Game()
    game.start_splash('B')
    for _ in range(STAGE_SPLASH_TIME + 1):
        game.update()

    boss = game.enemies[0]
    shots_fired = 0
    for i in range(500):
        before = len(game.bullets)
        game.update()
        after = len(game.bullets)
        if after > before:
            shots_fired += 1
    print(f"Boss fired {shots_fired} bullets in 500 ticks (expected > 0)")
    return shots_fired > 0

def test_armor_moves():
    print("=== Test: Stage 2 Armor tanks navigate ===")
    pygame.init()
    game = Game()
    game.start_splash(2)
    for _ in range(STAGE_SPLASH_TIME + 1):
        game.update()

    # Wait for enemies to spawn
    for _ in range(120):
        game.update()

    if not game.enemies:
        print("FAIL: No enemies spawned yet")
        return False

    start_positions = {id(e): (e.x, e.y) for e in game.enemies}

    for _ in range(300):
        game.update()

    moved = 0
    for e in game.enemies:
        sp = start_positions.get(id(e))
        if sp and (e.x, e.y) != sp:
            moved += 1

    total = len(game.enemies)
    print(f"{moved}/{total} enemies moved from starting position after 300 ticks")
    return moved > 0

if __name__ == "__main__":
    ok1 = test_boss_shoots()
    ok2 = test_armor_moves()
    print("\n=== RESULTS ===")
    print(f"Boss shoots: {'PASS' if ok1 else 'FAIL'}")
    print(f"Armor moves: {'PASS' if ok2 else 'FAIL'}")
    sys.exit(0 if ok1 and ok2 else 1)
