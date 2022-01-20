import asyncio
import threading
import time
from math import sqrt, inf

import pygame
from pygame import constants

import consts
from point_service import points
from util import on_event, on_key_released, intervalled, color, random_color

group_factor = 5
proximity_dist = 30

speed_coefficient = 2

draws_circles = False
do_dbscan = False


@on_event(consts.DRAWING)
def draw(surface, **kwargs):
    if draws_circles:
        for point in points:
            pygame.draw.circle(surface, point.color, (point.x, point.y), proximity_dist, width=1)

@on_key_released(constants.KSCAN_G)
def start_dbscan(**kwargs):
    x = threading.Thread(target=dbscan, args=[points])
    x.start()


@on_key_released(constants.KSCAN_C)
def toggle_drawing_circles():
    global draws_circles
    draws_circles = not draws_circles


def dist(point_a, point_b):
    return sqrt((point_a.x - point_b.x) ** 2 + (point_a.y - point_b.y) ** 2)


def prepared(target_points):
    # выстраивает точки для обхода в ширину, просто для красоты
    cache_points = [*target_points]
    all_points = [*target_points]
    prepared_points = []

    while len(cache_points) > 0:
        neighbours = [cache_points.pop(0)]

        for p1 in neighbours:
            p1.color = color('blue')
            for p2 in all_points:
                if p1 is p2:
                    continue

                if dist(p1, p2) <= proximity_dist:
                    if p2 not in neighbours:
                        cache_points.remove(p2)
                        neighbours.append(p2)

        prepared_points.extend(neighbours)
    return prepared_points


def dbscan(target_points):
    global do_dbscan
    if do_dbscan:
        return
    do_dbscan = True
    start = time.time()

    greens = []
    yellows = []

    # словарь, ключи - зеленые точки, значение - массив с желтыми точками
    # типо храню для желтых точек близжайшие зеленые
    boarded = {}

    cache_points = [*prepared(target_points)]
    interval = speed_coefficient / len(target_points)

    # ищем зеленые точки
    for point1 in intervalled(cache_points, interval):
        neighbour_count = 0
        for point2 in target_points:

            if point1 == point2:
                continue

            if dist(point1, point2) <= proximity_dist:
                neighbour_count += 1

        if neighbour_count >= group_factor:
            point1.color = color('green')
            greens.append(point1)

    # убираем точки из общего массива
    for green in greens:
        cache_points.remove(green)

    # находим желтые точки
    for point1 in intervalled(cache_points, interval):
        min_dist = inf
        nearest = None

        for point2 in target_points:

            if point1 == point2:
                continue

            if point2.color == color('green'):

                if dist(point1, point2) > proximity_dist:
                    continue

                current_dist = dist(point1, point2)
                if current_dist <= min_dist:
                    min_dist = current_dist
                    nearest = point2

        if nearest is not None:
            point1.color = color('yellow')
            yellows.append(point1)
            boarded.setdefault(nearest, []).append(point1)

    for yellow in yellows:
        cache_points.remove(yellow)

    asyncio.run(asyncio.sleep(1))

    # собираем зеленые в кластеры
    clusters = []
    while len(greens) > 0:
        cluster = [greens.pop(0)]

        for point1 in cluster:
            for point2 in greens:
                if point1 is point2:
                    continue

                if dist(point1, point2) <= proximity_dist:
                    if point2 not in cluster:
                        greens.remove(point2)
                        cluster.append(point2)

        # добавляем в кластер и желтые
        yellows_in_cluster = []
        for green in cluster:
            if green in boarded:
                yellows_in_cluster.extend(boarded[green])
        cluster.extend(yellows_in_cluster)
        clusters.append(cluster)

    # расскращиваем кластеры
    for cluster in clusters:
        rng_color = random_color()

        for p in intervalled(cluster, interval):
            p.color = rng_color

    end = time.time()
    print(f'Time: {end - start:.2f} sec')
    do_dbscan = False
