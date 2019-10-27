# -*- coding: utf-8 -*-

import os

import pygame
from pygame.locals import *  # NOQA

from agame.tiled import TiledFile
from agame.bgmgr import BackgroundManager
from agame.utils import constrain_to_range
from agame.entities import Player

from agame.constants import FPS
from agame.constants import SCREEN_COLS
from agame.constants import SCREEN_ROWS
from agame.constants import SPEED_X
from agame.constants import SPEED_Y
from agame.constants import GRAVITY


class Game:

    LAYERS = (
        ("cel", 0.025),
        ("montanyes", 0.1),
        ("decoracio", 1),
        ("plataforma", 1),
    )

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (SCREEN_COLS * 64, SCREEN_ROWS * 64)  # FIXME: hardcoded tile size
        )
        pygame.display.set_caption('Monkey Fever')

        self.clock = pygame.time.Clock()

        self.ts = TiledFile(
            os.path.join(
                os.path.dirname(__file__),
                "assets",
                "prova-platformer.json"
            )
        )
        self.background = BackgroundManager(
            (SCREEN_COLS, SCREEN_ROWS),
            self.ts,
            self.LAYERS,
        )
        debug_bg = pygame.Surface((4 * self.ts.tile_width, 2 * self.ts.tile_height))
        debug_bg.set_alpha(192)
        self.debug_bg = debug_bg.convert_alpha()

        pygame.font.init()
        self.myfont = pygame.font.SysFont('Ubuntu Mono', 16)

        self.debug = False
        # self.camera_x = SCREEN_COLS / 2
        # self.camera_y = SCREEN_ROWS / 2
        # self.vp_offset_x = self.camera_x - SCREEN_COLS / 2
        # self.vp_offset_y = self.camera_y - SCREEN_ROWS / 2
        self.player = Player(
            x=29.0,
            y=0.0,
            sprites=[
                # 7-9     : fantasma
                # 10-13   : carlota
                # 76-78   : ???
                # 98-100  : rabano
                # 115-117 : monigot
                self.ts.get_tile_by_index(115),
                self.ts.get_tile_by_index(116),
                self.ts.get_tile_by_index(117),
            ],
            width=self.ts.width,
            height=self.ts.height,
            plataforma=self.ts.get_layer_by_name("plataforma"),
        )

    def get_layer_name_by_index(self, n):
        return self.LAYERS[n][0]

    def main(self):

        self.quit = False

        while not self.quit:

            self.elapsed = self.clock.tick(FPS)

            for event in pygame.event.get():
                self.process_event(event)

            self.player.update(self.elapsed)

            self.vp_offset_x = constrain_to_range(
                self.player.x - SCREEN_COLS / 2,
                0,
                self.ts.width - SCREEN_COLS
            )

            self.vp_offset_y = constrain_to_range(
                self.player.y - SCREEN_ROWS / 2,
                0,
                self.ts.height - SCREEN_ROWS
            )

            self.camera_x = self.vp_offset_x + SCREEN_COLS / 2
            self.camera_y = self.vp_offset_y + SCREEN_ROWS / 2

            self.background.update(self.vp_offset_x, self.elapsed)

            self.screen.blit(self.background.get_background(), (0, 0))
            self.screen.blit(
                self.player.sprite,
                self.w2s(self.player.x, self.player.y)
            )

            if self.debug:
                self.display_debug_info()

            pygame.display.flip()

            pygame.display.set_caption("Monkey Fever: [%7.2f]" % self.clock.get_fps())

    def w2s(self, x, y):
        """World to screen.

        Converteix les coordenades ``(x, y)`` especificades en relació
        al sistema de coordenades del mon (tiles) en coordenades en
        relació a la pantalla (pixels).

        """
        return (
            (x - self.vp_offset_x) * self.ts.tile_width,
            (y - self.vp_offset_y) * self.ts.tile_height
        )

    def process_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.player.speed_x = -SPEED_X
            elif event.key == pygame.K_RIGHT:
                self.player.speed_x = SPEED_X
            elif event.key == pygame.K_UP:
                if self.player.touching_ground:
                    self.player.speed_y = -SPEED_Y
                    self.player.touching_ground = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.quit = True
            elif event.key == pygame.K_LEFT:
                self.player.speed_x = 0
            elif event.key == pygame.K_RIGHT:
                self.player.speed_x = 0
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                self.background.toggle_layer_visibility(
                    self.get_layer_name_by_index(event.key - pygame.K_1)
                )
            elif event.key == pygame.K_d:
                self.background.toggle_debug_mode()
                self.player.toggle_debug_mode()
                self.debug = not self.debug

    def display_debug_info(self):
        self.screen.blit(self.debug_bg, (8, 8))
        text = self.myfont.render("offset  = %8.4f" % self.vp_offset_x, False, (255, 255, 255))
        self.screen.blit(text, (12, 12))
        text = self.myfont.render(
            "player  = (%8.4f, %8.4f)" % (self.player.x, self.player.y),
            False,
            (255, 255, 255)
        )
        self.screen.blit(text, (12, 24))
        text = self.myfont.render(
            "camera  = (%8.4f, %8.4f)" % (self.camera_x, self.camera_y),
            False,
            (255, 255, 255)
        )
        self.screen.blit(text, (12, 36))
        text = self.myfont.render(
            "speed   = (%8.4f, %8.4f)" % (self.player.speed_x, self.player.speed_y),
            False,
            (255, 255, 255)
        )
        self.screen.blit(text, (12, 48))
        text = self.myfont.render("elapsed = %8.4f" % self.elapsed, False, (255, 255, 255))
        self.screen.blit(text, (12, 60))
        text = self.myfont.render("fps     = %8.4f" % self.clock.get_fps(), False, (255, 255, 255))
        self.screen.blit(text, (12, 72))
        text = self.myfont.render("gravity = %8.4f" % GRAVITY, False, (255, 255, 255))
        self.screen.blit(text, (12, 84))

        # HACK: açò hauria d'anar a un altre lloc
        foo = self.w2s(self.player.x, self.player.y)
        pygame.draw.rect(
            self.screen,
            (0, 255, 0),
            (foo[0], foo[1], self.ts.tile_width, self.ts.tile_height),
            1
        )


if __name__ == '__main__':
    game = Game()
    game.main()
