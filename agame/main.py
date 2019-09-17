# -*- coding: utf-8 -*-

import os
import time

import pygame
from pygame.locals import *  # NOQA

from agame.tiled import TiledFile

SCALE = 4


def main():
    pygame.init()
    screen = pygame.display.set_mode((20 * 16 * SCALE, 9 * 16 * SCALE))
    pygame.display.set_caption('Monkey Fever')

    ts = TiledFile(
        os.path.join(
            os.path.dirname(__file__),
            "assets",
            "prova-platformer.json"
        )
    )
    quit = False
    left = 0
    buffer = pygame.Surface((21 * 16, 9 * 16))
    speed_x = 1.0 / 60.0
    frames = 0
    t0 = time.time()
    while not quit:

        left = max(min(left + speed_x, ts.width - 20 - 1), 0)

        # TODO: if left no canviar no cal pintar res? ara no, pero si
        # hi ha personatges que es mouen i altres elements
        # probablement si ... pero si el gestor de background s'ho
        # curra (cache) no caldria.

        # TODO: l'ample (20) pot veure's incrementat (a 21) si es
        # mostra part d'un tile
        iteradors = [i.iter_rect(int(left), 0, 21, 9) for i in ts.layers]
        x = 0
        y = 0
        for tiles in zip(*iteradors):
            # print(tiles)
            for tile in tiles:
                if tile > 0:
                    buffer.blit(ts.get_tile_by_index(tile), (x, y))
            x += 16
            if x >= 21 * 16:
                x = 0
                y += 16

        sf = buffer.subsurface(
            pygame.Rect(int((left - int(left)) * 16), 0, 20 * 16, 9 * 16)
        )
        pygame.transform.scale(sf, screen.get_size(), screen)
        # screen.blit(buffer, (0, 0))
        pygame.display.flip()
        # time.sleep(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit = True
                elif event.key == pygame.K_SPACE:
                    speed_x = -speed_x
        # event = pygame.event.wait()
        # while event.type != KEYDOWN:
        #     event = pygame.event.wait()
        #     quit = True
        frames = frames + 1
        fps = frames / (time.time() - t0)
        pygame.display.set_caption("Monkey Fever: [%7.2f]" % fps)


if __name__ == '__main__':
    main()
