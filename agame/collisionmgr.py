# -*- coding: utf-8 -*-

# $Id:$

import abc


class CollisionManagerBase(abc.ABC):

    # NOTE: check_collision_xxx returns True iif there's a collision

    # TODO: no tinc clar si és preferible aquesta API o un únic mètode
    # que comprova tots els costats i retorna LEFT, RIGHT, UP, DOWN o
    # None

    def check_collision_left(self, x, y, width, height):
        pass

    def check_collision_right(self, x, y, width, height):
        pass

    def check_collision_up(self, x, y, width, height):
        pass

    def check_collision_down(self, x, y, width, height):
        pass


class PlatformCollisionManager(CollisionManagerBase):

    def __init__(self, map_):
        self._map = map_

    def check_collision_left(self, x, y, width, height):
        return self._map.get(x, y) != 0 \
            or self._map.get(x, y + height - 0.1) != 0

    def check_collision_right(self, x, y, width, height):
        return self._map.get(x + width, y) != 0 \
            or self._map.get(x + width, y + height - 0.1) != 0

    def check_collision_up(self, x, y, width, height):
        return self._map.get(x, y) != 0 \
            or self._map.get(x + width - 0.1, y) != 0

    def check_collision_down(self, x, y, width, height):
        return self._map.get(x, y + height) != 0 \
            or self._map.get(x + width - 0.1, y + height) != 0


class EntityCollisionManager(CollisionManagerBase):

    def __init__(self):
        self._entities = []

    def add_entity(self, entity):
        self._entities.append(entity)
