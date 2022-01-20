import random
from math import pi, sin, cos

import pygame

import consts
from util import on_event, on_key_released, color


class Point:
    def __init__(self, x, y, clr=None):
        if clr is None:
            clr = color('red')
        self.x = x
        self.y = y
        self.color = clr

    def __repr__(self):
        return str(self)

    def __iter__(self):
        for i in [self.x, self.y]:
            yield i

    def __hash__(self):
        return hash(tuple(self))

    def __str__(self):
        return f'Point({self.x:.2f}, {self.y:.2f})'


is_drawing = False
temp_point = 0

points = []

point_creation_speed = 25  # in sec

angle_range = [0, 2 * pi]
radius_range = [0, 15]


@on_event(pygame.MOUSEBUTTONDOWN)
def start_drawing(**kwargs):
    global is_drawing
    is_drawing = True


@on_event(pygame.MOUSEBUTTONUP)
def finish_drawing(**kwargs):
    global is_drawing
    is_drawing = False


@on_key_released(pygame.KSCAN_D)
def clear():
    points.clear()


@on_event(consts.DRAWING)
def draw(surface, **kwargs):
    for point in points:
        pygame.draw.circle(surface, point.color, (point.x, point.y), 3)


@on_event(consts.UPDATING)
def update_points(dt, **kwargs):
    global temp_point

    if is_drawing:
        temp_point += point_creation_speed * dt

    for i in range(int(temp_point)):
        add_point(*pygame.mouse.get_pos())

    temp_point -= int(temp_point)


def add_point(x, y):
    angle = random.uniform(*angle_range)
    radius = random.randint(*radius_range)
    points.append(Point(x + sin(angle) * radius, y + cos(angle) * radius))
