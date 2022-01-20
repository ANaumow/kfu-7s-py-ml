import sys

import pygame

import consts
from util import functions_by_type, on_event

import importlib

modules = ['point_service', 'dbscan_service']
for module in modules:
    globals().update(importlib.import_module(module).__dict__)

HEIGHT = 600
WIDTH = 800
FPS = 60
deltaTime = 0
game_loop = True

pygame.init()
FramePerSec = pygame.time.Clock()
surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DBSCAN example")


@on_event(pygame.QUIT)
def destroy_game(**kwargs):
    global game_loop
    game_loop = False


@on_event(consts.UPDATING)
def on_quit(**kwargs):
    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        destroy_game()


def post_event(event_type, event_body=None):
    if event_body is None:
        event_body = {}
    pygame.event.post(pygame.event.Event(event_type, event_body))


old_keys = tuple(pygame.key.get_pressed())
while game_loop:
    surface.fill((255, 255, 255))

    for index, value in enumerate(tuple(pygame.key.get_pressed())):
        if value == 0 and old_keys[index] == 1:
            post_event(pygame.USEREVENT + index)
    old_keys = tuple(pygame.key.get_pressed())

    post_event(consts.DRAWING, {'surface': surface})
    post_event(consts.UPDATING, {'dt': deltaTime})

    for event in pygame.event.get():
        for function in functions_by_type.get(event.type, []):
            function(**event.dict)

    pygame.display.update()
    deltaTime = FramePerSec.tick(FPS) / 1000.0

pygame.quit()
sys.exit()
