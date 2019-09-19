# -*- coding: utf-8 -*-

import os
import time

import pygame
from pygame.locals import *  # NOQA

from agame.tiled import TiledFile
from agame.bgmgr import BackgroundManager


SCALE = 4
SCREEN_COLS = 20
SCREEN_ROWS = 9


def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (SCREEN_COLS * 16 * SCALE, SCREEN_ROWS * 16 * SCALE)
    )
    pygame.display.set_caption('Monkey Fever')
    clock = pygame.time.Clock()

    ts = TiledFile(
        os.path.join(
            os.path.dirname(__file__),
            "assets",
            "prova-platformer.json"
        )
    )
    background = BackgroundManager(
        SCREEN_COLS,
        SCREEN_ROWS,
        ts,
        ("cel", "montanyes", "decoracio", "plataforma", "personatges"),
        (0.25, 0.5, 1, 1, 1),
    )
    quit = False
    left = 0
    speed_x = 1.0 / 120.0
    frames = 0
    t0 = time.time()
    while not quit:

        elapsed = clock.tick(120)
        left = max(min(left + speed_x * elapsed, ts.width - SCREEN_COLS - 1), 0)

        background.update(left, elapsed)

        pygame.transform.scale(background.get_background(), screen.get_size(), screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit = True
                elif event.key == pygame.K_SPACE:
                    speed_x = -speed_x

        frames = frames + 1
        fps = frames / (time.time() - t0)
        pygame.display.set_caption("Monkey Fever: [%7.2f]" % fps)


if __name__ == '__main__':
    main()
