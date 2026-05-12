import os, sys, pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'
sys.path.insert(0, os.path.abspath('.'))
from constants import *
pygame.init()

from main import Game

game = Game()
game.start_splash('B')
for _ in range(STAGE_SPLASH_TIME + 1):
    game.update()

boss = game.enemies[0]
player = game.player

total_shots = 0
for i in range(800):
    before = len(game.bullets)
    game.update()
    after = len(game.bullets)
    shots = after - before
    total_shots += max(0, shots)
    dist = abs(boss.x - player.x) + abs(boss.y - player.y)
    if i % 100 == 0:
        print(f"T={i}: boss=({boss.x},{boss.y}) player=({player.x},{player.y}) dist={dist} shots_this_tick={shots} total={total_shots} cd={boss.shoot_cooldown}")

print(f"\nTotal bullets fired in 800 ticks: {total_shots}")
