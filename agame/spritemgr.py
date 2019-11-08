# -*- coding: utf-8 -*-

# $Id:$

import pygame


class SpriteSheet:

    def __init__(self, path, tile_width, tile_height):
        self._path = path
        self._tile_width = tile_width
        self._tile_height = tile_height
        self._surface = pygame.image.load(path)
        self._num_horizontal_tiles = self._surface.get_width() // tile_width

    def get_sprite(self, start_index, end_index=None):
        if end_index is None:
            end_index = start_index
        x0 = start_index % self._num_horizontal_tiles
        y0 = start_index // self._num_horizontal_tiles
        xf = end_index % self._num_horizontal_tiles
        yf = end_index // self._num_horizontal_tiles
        return self._surface.subsurface(
            pygame.Rect(
                x0 * self._tile_width,
                y0 * self._tile_height,
                (xf - x0 + 1) * self._tile_width,
                (yf - y0 + 1) * self._tile_height,
            )
        )
