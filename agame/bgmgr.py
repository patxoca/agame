# -*- coding: utf-8 -*-

from typing import List
import pygame

from .tiled import TiledFile


class BackgroundManager:

    def __init__(self, cols: int, rows: int, tm: TiledFile, layer_names: List[str],
                 relative_speeds: List[float]):
        # layer_names: layers ordenats de més al fons a més al front

        # TODO: garantir que la mida del viewport es menor o igual que
        # el mapa
        self.vp_rows = rows
        self.vp_cols = cols
        self.tm = tm
        self.layer_names = layer_names
        self.layers = [tm.get_layer_by_name(i) for i in layer_names]

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

    def update(self, left, elapsed):
        # TODO: if left no canviar no cal pintar res? ara no, pero si
        # hi ha personatges que es mouen i altres elements
        # probablement si ... pero si el gestor de background s'ho
        # curra (cache) no caldria.

        # TODO: comprovar que left està dins els límits

        # TODO: l'ample (20) pot veure's incrementat (a 21) si es
        # mostra part d'un tile
        iteradors = [i.iter_rect(int(left), 0, self.buffer_cols, self.buffer_rows)
                     for i in self.layers]
        x = 0
        y = 0
        buffer = self.buffer
        gtbi = self.tm.get_tile_by_index
        for tiles in zip(*iteradors):
            # print(tiles)
            for tile in tiles:
                if tile > 0:
                    buffer.blit(gtbi(tile), (x, y))
            x += self.tile_width
            if x >= self.buffer_width:
                x = 0
                y += self.tile_height

        self.sf = buffer.subsurface(
            pygame.Rect(
                int((left - int(left)) * self.tile_width),
                0,
                self.vp_width,
                self.vp_height
            )
        )

    def get_background(self):
        return self.sf
