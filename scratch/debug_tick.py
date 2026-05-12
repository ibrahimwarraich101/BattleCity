import os, sys, pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
sys.path.insert(0, os.path.abspath('.'))
from constants import *
pygame.init()

from main import Game

game = Game()
game.start_splash(2)
for _ in range(STAGE_SPLASH_TIME + 1):
    game.update()

for i in range(250):
    game.update()
    for j, e in enumerate(game.enemies):
        if j == 0:  # Only track the first enemy
            print(f"Tick {i}: pos=({e.x},{e.y}) cd={e.move_cooldown} scd={e.shoot_cooldown} stuck={getattr(e, 'stuck_timer', 0)}")
