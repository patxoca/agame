# -*- coding: utf-8 -*-

import array
import base64
import json
import os
import zlib

import pygame


class TiledFile:

    def __init__(self, path: str):
        self.path = path
        self._load()
        self._tiles = {}

    def get_layer_by_name(self, name: str):
        for l in self.layers:
            if l.name == name:
                return l
        return None

    def get_tile_by_index(self, index: int):
        # retorna un tile donat l'índex global
        if index not in self._tiles:
            self._tiles[index] = None
            for ts in self.tile_sets:
                t = ts.get_tile_by_index(index)
                if t is not None:
                    self._tiles[index] = t
                    break
        return self._tiles[index]

    def _load(self):
        with open(self.path, "r") as f:
            self._data = json.load(f)

        d = self._data
        self.version = d["version"]
        self.height = d["height"]
        self.width = d["width"]
        self.next_object_id = d["nextobjectid"]
        self.orientation = d["orientation"]
        self.properties = d["properties"]
        self.render_order = d["renderorder"]
        self.tile_height = d["tileheight"]
        self.tile_width = d["tilewidth"]
        self.layers = [Layer(i) for i in d["layers"]]
        self.tile_sets = [TileSet(self, i) for i in d["tilesets"]]


class TileSet:

    def __init__(self, parent: TiledFile, data: dict):
        self._parent = parent
        self.first_gid = data["firstgid"]
        self.image_path = os.path.join(os.path.dirname(parent.path), data["image"])
        self.image_height = data["imageheight"]
        self.image_width = data["imagewidth"]
        self.margin = data["margin"]
        self.name = data["name"]
        self.properties = data["properties"]
        self.spacing = data["spacing"]
        self.tile_count = data["tilecount"]
        self.tile_height = data["tileheight"]
        self.tile_width = data["tilewidth"]
        self.transparent_color = data["transparentcolor"]

        self.last_gid = self.first_gid + data["tilecount"] - 1

        # TODO: interceptar errors al llegir la imatge
        self.image_data = pygame.image.load(self.image_path).convert_alpha()

        # TODO: tindre en compte el margin i spacing
        self.num_columns = self.image_width // self.tile_width
        self.num_rows = self.image_height // self.tile_height

        # cache pels tiles individuals. Mapeja un index local a una
        # instancia de pygame.Surface
        self._tiles = {}

    def get_tile_by_index(self, index: int):
        # retorna un tile a partir de l'index global
        if not (self.first_gid <= index <= self.last_gid):
            return None
        index = index - self.first_gid  # index local comptant des de zero
        if index not in self._tiles:
            x = index % self.num_columns
            y = index // self.num_columns
            r = pygame.Rect(
                x * self.tile_width, y * self.tile_height,
                self.tile_width, self.tile_height
            )
            self._tiles[index] = self.image_data.subsurface(r)
        return self._tiles[index]


class Layer:

    RIGHT_DOWN = 1
    DOWN_RIGHT = 2

    def __init__(self, data: dict):
        self.name = data["name"]
        self.data = self._extract_data(
            data["data"], data["encoding"], data["compression"],
            data["width"], data["height"]
        )
        self.height = data["height"]
        self.width = data["width"]
        self.opacity = data["opacity"]
        self.type_ = data["type"]
        self.visible = data["visible"]
        self.x = data["x"]
        self.y = data["y"]

    def get(self, x, y):
        offset = int(y) * self.width + int(x)
        return self.data[offset]

    def iter_rect(self, x: int, y: int, width: int, height: int, order=RIGHT_DOWN):
        # x,y coordenada superior esquerra, basada en 0

        # TODO: clip de rang

        # TODO: implementar DOWN_RIGHT

        for yy in range(y, y + height):
            xx = yy * self.width + x
            for xx in range(xx, xx + width):
                yield self.data[xx]

    def _extract_data(self, data: bytes, enc: str, comp: str, width: int, height: int):
        # TODO: suportar altres formats
        assert enc == "base64"
        assert comp == "zlib"
        d = zlib.decompress(base64.b64decode(data))

        # TODO: no tinc clar com/si "renderorder" afecta l'ordre en
        # que s'enumeren els tiles dins el layer. És una propietat del
        # tileset. Pel moment s'assumeix que els tiles s'enumeren
        # seguint l'ordre "right-down". Si cal, sembla que aquest
        # seria un bon lloc per normalizar l'ordre.
        return array.array("I", d)
