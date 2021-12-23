import sys

import pygame

import random
from math import sqrt, inf, pi, sin, cos

# количество точек, которое должно быть рядом чтобы рассматриваяемая нами точка
# считалась находящейся в группе, такие точки образую кластер
group_factor = 3

sx = 8
sy = 8

size_x = 28
size_y = 28 * 3

card_x = size_x * 2
card_y = size_x * 4

# расстояние, на котором две точки считаются близкими друг к другу
proximity_dist = sx * 2


def dist(point_a, point_b):
    return sqrt((point_a.x - point_b.x) ** 2 + (point_a.y - point_b.y) ** 2)


def random_color():
    return [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]


cache_colors = []


def color_for_cluster(index):
    if index >= len(cache_colors):
        # добавляем сколько нужно еще, если нужны новые цвета
        for i in range(len(cache_colors) - index + 1):
            cache_colors.append(random_color())

    return cache_colors[index]


def dbscan(target_points):
    greens = []
    yellows = []

    # словарь, ключи - зеленые точки, значение - массив с желтыми точками
    # типо храню для желтых точек близжайшие зеленые
    boarded = {}

    # копируем точки в свой массив, чтоб можно было удалять
    cache_points = [*target_points]

    # ищем зеленые точки
    for point1 in cache_points:
        neighbour_count = 0
        for point2 in target_points:

            if point1 == point2:
                continue

            if dist(point1, point2) <= proximity_dist:
                neighbour_count += 1

        if neighbour_count >= group_factor:
            point1.color = 'green'
            greens.append(point1)

    # убираем зеленые точки из общего массива
    for green in greens:
        cache_points.remove(green)

    # находим желтые точки
    for point1 in cache_points:
        min_dist = inf
        nearest = None

        for point2 in target_points:

            if point1 == point2:
                continue

            if point2.color == 'green':

                if dist(point1, point2) > proximity_dist:
                    continue

                current_dist = dist(point1, point2)
                if current_dist <= min_dist:
                    min_dist = current_dist
                    nearest = point2

        if nearest is not None:
            point1.color = 'yellow'
            yellows.append(point1)
            boarded.setdefault(nearest, []).append(point1)

    # удаляем желтые точки из общего массива
    for yellow in yellows:
        cache_points.remove(yellow)

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
    for cluster_index, cluster in enumerate(clusters):
        rng_color = color_for_cluster(cluster_index)

        for p in cluster:
            p.color = rng_color

    return clusters


class Point:
    def __init__(self, x, y, clr=None):
        if clr is None:
            clr = 'red'
        self.x = x
        self.y = y
        self.color = clr

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __iter__(self):
        for i in [self.x, self.y]:
            yield i

    def __hash__(self):
        return hash(tuple(self))

    def __str__(self):
        return f'Point({self.x:.2f}, {self.y:.2f})'


# настройки для генерации точек
point_to_create_per_click = 5
angle_range = [0, 2 * pi]
radius_range = [0, 15]

points = set()

_clusters = []


def add_points(x, y):
    point = Point(int(x / sx) * sx, int(y / sy) * sy)

    if not (point in points):
        points.add(point)
        global _clusters
        _clusters = dbscan(points)


FPS = 60

pygame.init()
FramePerSec = pygame.time.Clock()

# разрешение окошка
HEIGHT = 600
WIDTH = 800
surface = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Example")

game_loop = True
while game_loop:
    surface.fill((255, 255, 255))

    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
        game_loop = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_loop = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k:
                fields = []

                for cluster in sorted(_clusters, key=lambda c: min(c, key=lambda p: p.x).x):

                    field = [[0 for y in range(28)] for x in range(28)]
                    min_x = min(cluster, key=lambda p: p.x).x
                    max_x = max(cluster, key=lambda p: p.x).x

                    min_y = min(cluster, key=lambda p: p.y).y
                    max_y = max(cluster, key=lambda p: p.y).y

                    dif_x = max_x - min_x
                    dif_y = max_y - min_y

                    for point in cluster:
                        x = int((point.x - min_x + (28 * sx - dif_x) / 2) / sx)
                        y = int((point.y - min_y + (28 * sy - dif_y) / 2) / sy)

                        if x in range(0, 27) and y in range(0, 27):
                            field[x][y] = 1

                    fields.append(field)

                print(fields)

    if any(pygame.mouse.get_pressed()):
        add_points(*pygame.mouse.get_pos())

    for point in points:
        pygame.draw.rect(surface, point.color, pygame.Rect(point.x, point.y, sx, sy))

    pygame.display.update()

pygame.quit()
sys.exit()
