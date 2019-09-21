# -*- coding: utf-8 -*-

from typing import List
from typing import Tuple
import pygame

from .tiled import TiledFile
from .utils import constraint_to_range


class _LayerInfo:
    def __init__(self,
                 name: str,
                 tilemap: TiledFile,
                 speed: float,
                 visible: bool = True):
        self.name = name
        self.tilemap = tilemap
        self.speed = speed
        self.visible = visible


class BackgroundManager:

    def __init__(self,
                 size: Tuple[int, int],
                 tm: TiledFile,
                 layer_info: List[Tuple[str, float]]):
        # layer_names: layers ordenats de més al fons a més al front

        self.vp_rows = size[1]
        self.vp_cols = size[0]
        if self.vp_rows > tm.height or self.vp_cols > tm.width:
            raise ValueError(
                "Viewport size (%i, %i) out of bounds." % size
            )
        self.tm = tm

        layers = []
        for name, speed in layer_info:
            layer = self.tm.get_layer_by_name(name)
            if layer is None:
                raise ValueError("Layer not found '%s'." % name)
            layers.append(_LayerInfo(name, layer, speed, True))
        self.layers = layers

        self.tile_width = tm.tile_width
        self.tile_height = tm.tile_height
        # drawing buffer dimensions
        self.buffer_cols = self.vp_cols + 1
        self.buffer_rows = self.vp_rows
        self.buffer_width = self.buffer_cols * self.tile_width
        self.buffer_height = self.buffer_rows * self.tile_height
        # viewport dimensions
        self.vp_width = self.vp_cols * self.tile_width
        self.vp_height = self.vp_rows * self.tile_height
        self.buffer = pygame.Surface((self.buffer_width, self.buffer_height))
        self.sf = self.buffer.subsurface(
            pygame.Rect(self.tile_width, 0, self.vp_width, self.vp_height)
        )

        self.max_offset_x = self.tm.width - self.vp_cols
        self.dirty = True
        self.debug = False
        self.last_left = None

        self.font = pygame.font.SysFont("Ubuntu Mono", 10)

    def update(self, left: float, elapsed: float):
        left = constraint_to_range(left, 0, self.max_offset_x)
        if (left == self.last_left) and not self.dirty:
            return

        self.last_left = left
        self.dirty = False

        buffer = self.buffer
        buffer.fill((150, 150, 150))  # HACK: per facilitar la
                                      # depuració quan s'amaguen els
                                      # layers. Preferiria el patró de
                                      # "transparent"
        gtbi = self.tm.get_tile_by_index
        for layer in self.layers:
            if not layer.visible:
                continue
            ll = left * layer.speed
            offset_x = int(self.tile_width * (1 - (ll - int(ll))))
            x = offset_x
            y = 0
            cols = self.buffer_cols
            if offset_x == self.tile_width:
                # no fractional tile drawn
                cols = cols - 1
            it = layer.tilemap.iter_rect(int(ll), 0, cols, self.buffer_rows)
            for tile in it:
                if tile > 0:
                    buffer.blit(gtbi(tile), (x, y))
                    if self.debug:
                        text = self.font.render("%3i" % tile, False, (0, 0, 0))
                        buffer.blit(text, (x + 3, y + 2))
                        pygame.draw.rect(
                            buffer, (255, 0, 0), (x, y, self.tile_width, self.tile_height), 1
                        )
                x += self.tile_width
                if x >= self.buffer_width:
                    x = offset_x
                    y += self.tile_height

    def get_background(self):
        return self.sf

    def toggle_layer_visibility(self, name):
        for layer in self.layers:
            if layer.name == name:
                layer.visible = not layer.visible
                self.dirty = True
                return

        print("Layer '%s' does not exist." % name)

    def toggle_debug_mode(self):
        self.debug = not self.debug
        self.dirty = True
