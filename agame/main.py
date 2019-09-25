# -*- coding: utf-8 -*-

import os

import pygame
from pygame.locals import *  # NOQA

from agame.tiled import TiledFile
from agame.bgmgr import BackgroundManager


FPS = 120
SCREEN_COLS = 20
SCREEN_ROWS = 9
SPEED_X = 1.0 / 64.0


def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (SCREEN_COLS * 64, SCREEN_ROWS * 64)  # FIXME: hardcoded tile size
    )
    pygame.display.set_caption('Monkey Fever')
    # TODO: instead of "set_delay" may be use "get_pressed"?
    pygame.key.set_repeat(10, 50)
    clock = pygame.time.Clock()

    layers = (
        ("cel", 0.025),
        ("montanyes", 0.1),
        ("decoracio", 1),
        ("plataforma", 1),
    )

    def get_layer_name_by_index(n):
        return layers[n][0]

    ts = TiledFile(
        os.path.join(
            os.path.dirname(__file__),
            "assets",
            "prova-platformer.json"
        )
    )
    background = BackgroundManager(
        (SCREEN_COLS, SCREEN_ROWS),
        ts,
        layers,
    )
    debug_bg = pygame.Surface((4 * ts.tile_width, 2 * ts.tile_height))
    debug_bg.set_alpha(192)
    debug_bg = debug_bg.convert_alpha()

    pygame.font.init()
    myfont = pygame.font.SysFont('Ubuntu Mono', 16)

    debug = False
    mode = "normal"  # "step"
    quit = False
    save_speed_x = SPEED_X
    elapsed = 1
    camera_x = SCREEN_COLS / 2
    camera_y = SCREEN_ROWS / 2
    vp_offset_x = camera_x - SCREEN_COLS / 2
    vp_offset_y = camera_y - SCREEN_ROWS / 2
    player_x = 0.0
    player_y = 7.0
    if mode == "step":
        speed_x = 1
    else:
        speed_x = SPEED_X
    speed_y = SPEED_X

    player_sprite = ts.get_tile_by_index(115)

    while not quit:

        if mode != "step":
            elapsed = clock.tick(FPS)
        else:
            clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit = True
                elif event.key == pygame.K_LEFT:
                    player_x -= speed_x * elapsed
                    if player_x < 0:
                        player_x = 0
                elif event.key == pygame.K_RIGHT:
                    player_x += speed_x * elapsed
                    if player_x + 1 > ts.width:
                        player_x = ts.width - 1
                elif event.key == pygame.K_UP:
                    player_y -= speed_y * elapsed
                    if player_y < 0:
                        player_y = 0
                elif event.key == pygame.K_DOWN:
                    player_y += speed_y * elapsed
                    if player_y + 1 > ts.height:
                        player_y = ts.height - 1
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    background.toggle_layer_visibility(
                        get_layer_name_by_index(event.key - pygame.K_1)
                    )
                elif event.key == pygame.K_d:
                    background.toggle_debug_mode()
                    debug = not debug
                elif event.key == pygame.K_m:
                    if mode == "step":
                        mode = "normal"
                        speed_x = save_speed_x
                    else:
                        mode = "step"
                        save_speed_x = speed_x
                        speed_x = 1
                elif event.key == pygame.K_SPACE:
                    if mode == "step":
                        elapsed = 1 / ts.tile_width

        vp_offset_x = player_x - SCREEN_COLS / 2
        if vp_offset_x < 0:
            vp_offset_x = 0
        elif vp_offset_x > ts.width - SCREEN_COLS - 1:
            vp_offset_x = ts.width - SCREEN_COLS - 1
        camera_x = vp_offset_x + SCREEN_COLS / 2
        # vp_offset_x = 0

        # max(min(vp_offset_x + speed_x * elapsed, ts.width - SCREEN_COLS - 1), 0)

        background.update(vp_offset_x, elapsed)

        screen.blit(background.get_background(), (0, 0))
        screen.blit(
            player_sprite,
            (
                (player_x - vp_offset_x) * ts.tile_width,
                (player_y - vp_offset_y) * ts.tile_height
            )
        )

        if debug:
            screen.blit(debug_bg, (8, 8))
            text = myfont.render("offset  = %8.4f" % vp_offset_x, False, (255, 255, 255))
            screen.blit(text, (12, 12))
            text = myfont.render(
                "player  = (%8.4f, %8.4f)" % (player_x, player_y),
                False,
                (255, 255, 255)
            )
            screen.blit(text, (12, 24))
            text = myfont.render(
                "camera  = (%8.4f, %8.4f)" % (camera_x, camera_y),
                False,
                (255, 255, 255)
            )
            screen.blit(text, (12, 36))
            text = myfont.render("speed   = %8.4f" % speed_x, False, (255, 255, 255))
            screen.blit(text, (12, 48))
            text = myfont.render("elapsed = %8.4f" % elapsed, False, (255, 255, 255))
            screen.blit(text, (12, 60))
            text = myfont.render("fps     = %8.4f" % clock.get_fps(), False, (255, 255, 255))
            screen.blit(text, (12, 72))
        pygame.display.flip()

        pygame.display.set_caption("Monkey Fever: [%7.2f]" % clock.get_fps())
        elapsed = 0


if __name__ == '__main__':
    main()
