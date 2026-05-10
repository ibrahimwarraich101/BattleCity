import os
import sys
import pygame
import copy

os.environ['SDL_VIDEODRIVER'] = 'dummy'
sys.path.append(os.path.abspath('.'))

from agents.boss_tank_agent import BossAgent
from tank import BossTank, PlayerTank
from game_map import GameMap
from constants import *

def test_minimax():
    print("Starting Minimax Pruning Test...")
    pygame.init()
    
    # Setup dummy game state
    gmap = GameMap('B')
    boss = BossTank(BOSS_SPAWN[0], BOSS_SPAWN[1])
    player = PlayerTank(BOSS_PLAYER_SPAWN[0], BOSS_PLAYER_SPAWN[1])
    
    game_state = {
        'grid': gmap.grid,
        'boss': boss,
        'player': player,
        'eagle_pos': EAGLE_POS,
        'tanks': [boss, player],
        'bullets': []
    }
    
    agent = BossAgent()
    
    # Test at different HP levels (Phase 1, 2, 3)
    results = []
    for hp in [10, 5, 2]:
        boss.hp = hp
        action, n_raw, n_pruned = agent.decide(boss, game_state)
        depth = agent.get_phase(hp)['depth']
        print(f"HP {hp} (Depth {depth}): Raw={n_raw}, Pruned={n_pruned}")
        results.append(n_pruned < n_raw)

    if any(results):
        print("Minimax Pruning Test: PASSED (Pruning occurred in at least one case)")
        return True
    else:
        print("FAILED: Pruning never reduced node count!")
        return False

if __name__ == "__main__":
    if test_minimax():
        sys.exit(0)
    else:
        sys.exit(1)
