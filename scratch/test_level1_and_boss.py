import os, sys, pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
sys.path.insert(0, os.path.abspath('.'))

from main import Game
from tank import EnemyTank
from constants import *

def test_basic_tank_movement():
    """Test basic tank movement (Level 1)"""
    print("=== Test: Basic Tank Movement (Level 1) ===")
    pygame.init()
    game = Game()
    game.level = 1
    game.reset_level()
    
    # Spawn a basic tank directly
    basic_tank = EnemyTank(0, 0, 'basic')
    game.enemies = [basic_tank]
    
    start_pos = (basic_tank.x, basic_tank.y)
    
    # Simulate for a period
    for _ in range(300):
        game.update()
    
    end_pos = (basic_tank.x, basic_tank.y)
    distance = abs(end_pos[0] - start_pos[0]) + abs(end_pos[1] - start_pos[1])
    
    print(f"Basic tank: {start_pos} -> {end_pos}, distance={distance}")
    return distance > 0

def test_boss_fight():
    """Test boss tank movement and firing"""
    print("\n=== Test: Boss Tank Fighting ===")
    pygame.init()
    game = Game()
    game.start_splash('B')
    for _ in range(STAGE_SPLASH_TIME + 1):
        game.update()
    
    if not game.enemies:
        print("FAIL: No boss spawned")
        return False
    
    boss = game.enemies[0]
    print(f"Boss HP: {boss.hp}")
    
    # Check boss can move
    start_pos = (boss.x, boss.y)
    for _ in range(100):
        game.update()
    end_pos = (boss.x, boss.y)
    
    moved = start_pos != end_pos
    print(f"Boss moved: {moved} ({start_pos} -> {end_pos})")
    
    # Check boss can shoot
    shots_before = len(game.bullets)
    for _ in range(400):
        game.update()
    shots_after = len(game.bullets)
    
    print(f"Boss fired: {shots_after - shots_before} bullets in 400 ticks")
    
    return moved or (shots_after > shots_before)

if __name__ == "__main__":
    ok1 = test_basic_tank_movement()
    ok2 = test_boss_fight()
    
    print("\n=== RESULTS ===")
    print(f"Level 1 basic tank: {'PASS' if ok1 else 'FAIL'}")
    print(f"Boss stage: {'PASS' if ok2 else 'FAIL'}")
    
    sys.exit(0 if ok1 and ok2 else 1)
