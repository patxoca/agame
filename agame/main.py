# -*- coding: utf-8 -*-

import os

import pygame
from pygame.locals import *  # NOQA

from agame.tiled import TiledFile
from agame.bgmgr import BackgroundManager
from agame.utils import constrain_to_range


FPS = 120
SCREEN_COLS = 20
SCREEN_ROWS = 9
SPEED_X = 1.0 / 128.0
SPEED_Y = 1.0 / 64.0


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
        self.plataforma = self.ts.get_layer_by_name("plataforma")
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
        self.player_x = 90.0
        self.player_y = 7.0
        self.speed_x = 0
        self.speed_y = 0

        self.player_sprite = self.ts.get_tile_by_index(115)

    def get_layer_name_by_index(self, n):
        return self.LAYERS[n][0]

    def main(self):

        self.quit = False

        while not self.quit:

            self.elapsed = self.clock.tick(FPS)

            for event in pygame.event.get():
                self.process_event(event)

            self.update_player()

            self.vp_offset_x = constrain_to_range(
                self.player_x - SCREEN_COLS / 2,
                0,
                self.ts.width - SCREEN_COLS
            )

            self.vp_offset_y = constrain_to_range(
                self.player_y - SCREEN_ROWS / 2,
                0,
                self.ts.height - SCREEN_ROWS
            )

            self.camera_x = self.vp_offset_x + SCREEN_COLS / 2
            self.camera_y = self.vp_offset_y + SCREEN_ROWS / 2

            self.background.update(self.vp_offset_x, self.elapsed)

            self.screen.blit(self.background.get_background(), (0, 0))
            self.screen.blit(
                self.player_sprite,
                self.w2s(self.player_x, self.player_y)
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
                self.speed_x = -SPEED_X
            elif event.key == pygame.K_RIGHT:
                self.speed_x = SPEED_X
            elif event.key == pygame.K_UP:
                # FIXME: si és un salt caldria definir una velocitat
                # inicial i una acceleració de frenada (gravetat)
                self.speed_y = -SPEED_Y
            elif event.key == pygame.K_DOWN:
                # FIXME: no sembla que K_DOWN tingui sentit
                self.speed_y = SPEED_Y
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                self.quit = True
            elif event.key == pygame.K_LEFT:
                self.speed_x = 0
            elif event.key == pygame.K_RIGHT:
                self.speed_x = 0
            elif event.key == pygame.K_UP:
                # FIXME: no sembla que K_UP tingui sentit
                self.speed_y = 0
            elif event.key == pygame.K_DOWN:
                # FIXME: no sembla que K_DOWN tingui sentit
                self.speed_y = 0
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                self.background.toggle_layer_visibility(
                    self.get_layer_name_by_index(event.key - pygame.K_1)
                )
            elif event.key == pygame.K_d:
                self.background.toggle_debug_mode()
                self.debug = not self.debug

    def update_player(self):
        new_player_x = constrain_to_range(
            self.player_x + self.speed_x * self.elapsed,
            0,
            self.ts.width - 1
        )
        if self.speed_x < 0:
            if self.plataforma.get(new_player_x, self.player_y) == 0 and self.plataforma.get(new_player_x, self.player_y + 0.9) == 0:
                self.player_x = new_player_x
            else:
                self.player_x = int(new_player_x) + 1
        elif self.speed_x > 0:
            if self.plataforma.get(new_player_x + 1, self.player_y) == 0 and self.plataforma.get(new_player_x + 1, self.player_y + 0.9) == 0:
                self.player_x = new_player_x
            else:
                self.player_x = int(new_player_x)

        new_player_y = constrain_to_range(
            self.player_y + self.speed_y * self.elapsed,
            0,
            self.ts.height - 1
        )
        if self.speed_y < 0:
            if self.plataforma.get(self.player_x, new_player_y) == 0 and self.plataforma.get(self.player_x + 0.9, new_player_y) == 0:
                self.player_y = new_player_y
            else:
                self.player_y = int(new_player_y) + 1
        elif self.speed_y > 0:
            if self.plataforma.get(self.player_x, new_player_y + 1) == 0 and self.plataforma.get(self.player_x + 0.9, new_player_y + 1) == 0:
                self.player_y = new_player_y
            else:
                self.player_y = int(new_player_y)

    def display_debug_info(self):
        self.screen.blit(self.debug_bg, (8, 8))
        text = self.myfont.render("offset  = %8.4f" % self.vp_offset_x, False, (255, 255, 255))
        self.screen.blit(text, (12, 12))
        text = self.myfont.render(
            "player  = (%8.4f, %8.4f)" % (self.player_x, self.player_y),
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
        text = self.myfont.render("speed   = %8.4f" % self.speed_x, False, (255, 255, 255))
        self.screen.blit(text, (12, 48))
        text = self.myfont.render("elapsed = %8.4f" % self.elapsed, False, (255, 255, 255))
        self.screen.blit(text, (12, 60))
        text = self.myfont.render("fps     = %8.4f" % self.clock.get_fps(), False, (255, 255, 255))
        self.screen.blit(text, (12, 72))

        # HACK: açò hauria d'anar a un altre lloc
        foo = self.w2s(self.player_x, self.player_y)
        pygame.draw.rect(
            self.screen,
            (0, 255, 0),
            (foo[0], foo[1], self.ts.tile_width, self.ts.tile_height),
            1
        )


if __name__ == '__main__':
    game = Game()
    game.main()
