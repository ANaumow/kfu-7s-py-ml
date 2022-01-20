import asyncio
import random

import pygame

functions_by_type = {}


def on_event(event_type):
    def decorator(func):
        functions_by_type.setdefault(event_type, []).append(func)
        return func

    return decorator


def on_key_released(raw_key):
    return on_event(pygame.USEREVENT + raw_key)


def intervalled(__iterable, interval):
    for item in __iterable:
        asyncio.run(asyncio.sleep(interval))
        yield item

a = intervalled([], 0.1)


def random_color():
    return [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]


def color(name):
    if name == 'green':
        return [0, 255, 0]
    if name == 'yellow':
        return [255, 216, 0]
    if name == 'red':
        return [255, 0, 0]
    if name == 'blue':
        return [0, 0, 255]
