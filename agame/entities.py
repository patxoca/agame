# -*- coding: utf-8 -*-

# $Id:$

import abc

from .constants import SPEED_Y
from .constants import GRAVITY
from .utils import constrain_to_range


class EntityBase(abc.ABC):

    def update(self, elapsed):
        raise NotImplementedError()

    def draw(self):
        raise NotImplementedError()

    def enable_debug_mode(self):
        self._debug = True

    def disable_debug_mode(self):
        self._debug = False

    def toggle_debug_mode(self):
        self._debug = not self._debug


class Player(EntityBase):

    def __init__(self, x, y, sprite, width, height, plataforma):
        self.x = x
        self.y = y
        self.speed_x = 0
        self.speed_y = 0
        self.touching_ground = True

        # FIXME: millorar la integració
        self.sprite = sprite
        self.width = width
        self.height = height
        self.plataforma = plataforma

        self._debug = False

    def update(self, elapsed):
        new_player_x = constrain_to_range(
            self.x + self.speed_x * elapsed,
            0,
            self.width - 1
        )
        if self.speed_x < 0:
            # left
            if self.plataforma.get(new_player_x, self.y) == 0 and self.plataforma.get(new_player_x, self.y + 0.9) == 0:
                self.x = new_player_x
            else:
                # collision
                self.x = int(new_player_x) + 1
                # self.speed_x = 0
        elif self.speed_x > 0:
            # right
            if self.plataforma.get(new_player_x + 1, self.y) == 0 and self.plataforma.get(new_player_x + 1, self.y + 0.9) == 0:
                self.x = new_player_x
            else:
                # collision
                self.x = int(new_player_x)
                # self.speed_x = 0

        self.speed_y = constrain_to_range(
            self.speed_y - GRAVITY * elapsed,
            -SPEED_Y,
            4 * SPEED_Y
        )
        new_player_y = constrain_to_range(
            self.y + self.speed_y * elapsed,
            0,
            self.height - 1
        )
        if self.speed_y < 0:
            # up
            if self.plataforma.get(self.x, new_player_y) == 0 and self.plataforma.get(self.x + 0.9, new_player_y) == 0:
                self.y = new_player_y
            else:
                # collision
                self.y = int(new_player_y) + 1
                self.speed_y = 0
        elif self.speed_y > 0:
            # down
            if self.plataforma.get(self.x, new_player_y + 1) == 0 and self.plataforma.get(self.x + 0.9, new_player_y + 1) == 0:
                self.y = new_player_y
                self.touching_ground = False
            else:
                # collision
                self.y = int(new_player_y)
                self.speed_y = 0
                self.touching_ground = True
