# -*- coding: utf-8 -*-

# $Id:$

import abc

from .constants import SPEED_Y
from .constants import GRAVITY
from .utils import constrain_to_range


class AnimationBase(abc.ABC):

    def stop(self):
        pass

    def update(self, elapsed):
        pass


# NOTE: la implementació actual de l'animació probablement sap més del
# que li cal. En la seva forma més simple una animació és UNA
# seqüència de sprites. El jugador hauria de tindre varies seqüències
# animades (caminar dreta/esquerra, correr dreta/esquerra, saltar
# dreta/esquerra, esperar aturat ...) i triar la que toca en cada
# moment enlloc de que la seqüència sigui la que tria el joc de
# sprites.

class PlayerAnimation(AnimationBase):
    DIR_LEFT = 1
    DIR_RIGHT = 2

    FRAME_RATE = 75

    def __init__(self, sprites_left, sprites_right):
        self._sprites_left = sprites_left
        self._sprites_right = sprites_right
        self._elapsed = 0.0
        self._direction = self.DIR_RIGHT
        self._jumping = False

    def stop(self):
        self._elapsed = 0.0

    def update(self, elapsed, direction, jumping):
        if self._direction != direction:
            self._elapsed = 0
            self._direction = direction
        self._elapsed += elapsed
        self._jumping = jumping

    def get_sprite(self):
        if self._direction == self.DIR_RIGHT:
            active_sprites = self._sprites_right
        else:
            active_sprites = self._sprites_left
        if self._jumping:
            index = 0
        else:
            index = (int(self._elapsed) // self.FRAME_RATE) % len(active_sprites)
        return active_sprites[index]


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

    def __init__(self, x, y, animation, world_size, player_size, collision_manager):
        self.x = x
        self.y = y
        self.speed_x = 0
        self.speed_y = 0
        self.touching_ground = True

        self._animation = animation
        self.world_width, self.world_height = world_size
        self.player_width, self.player_height = player_size
        self._collmgr = collision_manager

        self._debug = False

    @property
    def sprite(self):
        return self._animation.get_sprite()

    def update(self, elapsed):
        # FIXME: el codi asumeix sprites 1 tile x 1 tile, la mida la
        # sap _animation
        direction = None
        new_player_x = constrain_to_range(
            self.x + self.speed_x * elapsed,
            0,
            self.world_width - 1
        )
        if self.speed_x < 0:
            # left
            # self._elapsed_moving += elapsed
            direction = PlayerAnimation.DIR_LEFT
            if self._collmgr.check_collision_left(new_player_x, self.y, self.player_width, self.player_height):
                # collision
                self.x = int(new_player_x) + self.player_width
                # self.speed_x = 0
            else:
                self.x = new_player_x
        elif self.speed_x > 0:
            direction = PlayerAnimation.DIR_RIGHT
            # self._elapsed_moving += elapsed
            # right
            if self._collmgr.check_collision_right(new_player_x, self.y, self.player_width, self.player_height):
                # collision
                self.x = int(new_player_x)
                # self.speed_x = 0
            else:
                self.x = new_player_x
        else:
            direction = None

        self.speed_y = constrain_to_range(
            self.speed_y - GRAVITY * elapsed,
            -SPEED_Y,
            4 * SPEED_Y
        )
        new_player_y = constrain_to_range(
            self.y + self.speed_y * elapsed,
            0,
            self.world_height - 1
        )
        if self.speed_y < 0:
            # up
            if self._collmgr.check_collision_up(self.x, new_player_y, self.player_width, self.player_height):
                # collision
                self.y = int(new_player_y) + self.player_height
                self.speed_y = 0
            else:
                self.y = new_player_y
        elif self.speed_y > 0:
            # down
            if self._collmgr.check_collision_down(self.x, new_player_y, self.player_width, self.player_height):
                # collision
                self.y = int(new_player_y)
                self.speed_y = 0
                self.touching_ground = True
            else:
                self.y = new_player_y
                self.touching_ground = False

        if direction is None:
            self._animation.stop()
        else:
            self._animation.update(elapsed, direction, not self.touching_ground)
