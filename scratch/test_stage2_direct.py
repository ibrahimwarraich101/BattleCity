import os, sys, pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
sys.path.insert(0, os.path.abspath('.'))

from main import Game
from tank import EnemyTank
from constants import *

def test_armor_direct():
    """Test armor tank movement directly (not spawned through normal game flow)"""
    print("=== Direct Test: Armor Tank Movement ===")
    pygame.init()
    game = Game()
    game.level = 2
    game.reset_level()
    
    # Spawn an armor tank directly
    armor_tank = EnemyTank(5, 5, 'armor')
    game.enemies = [armor_tank]
    
    print(f"Armor tank spawned at ({armor_tank.x}, {armor_tank.y})")
    start_pos = (armor_tank.x, armor_tank.y)
    
    # Simulate for a period
    for _ in range(300):
        game.update()
    
    end_pos = (armor_tank.x, armor_tank.y)
    distance = abs(end_pos[0] - start_pos[0]) + abs(end_pos[1] - start_pos[1])
    
    print(f"After 300 ticks: pos={end_pos}, distance moved={distance}")
    return distance > 0

def test_power_direct():
    """Test power tank movement directly (uses armor agent)"""
    print("\n=== Direct Test: Power Tank Movement ===")
    pygame.init()
    game = Game()
    game.level = 2
    game.reset_level()
    
    # Spawn a power tank directly
    power_tank = EnemyTank(5, 5, 'power')
    game.enemies = [power_tank]
    
    print(f"Power tank spawned at ({power_tank.x}, {power_tank.y})")
    start_pos = (power_tank.x, power_tank.y)
    
    # Simulate for a period
    for _ in range(300):
        game.update()
    
    end_pos = (power_tank.x, power_tank.y)
    distance = abs(end_pos[0] - start_pos[0]) + abs(end_pos[1] - start_pos[1])
    
    print(f"After 300 ticks: pos={end_pos}, distance moved={distance}")
    return distance > 0

if __name__ == "__main__":
    ok1 = test_armor_direct()
    ok2 = test_power_direct()
    
    print("\n=== RESULTS ===")
    print(f"Armor tank moves: {'PASS' if ok1 else 'FAIL'}")
    print(f"Power tank moves: {'PASS' if ok2 else 'FAIL'}")
    
    sys.exit(0 if ok1 and ok2 else 1)
