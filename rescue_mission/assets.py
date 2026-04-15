from pathlib import Path

import pygame

from . import config


def _clamp_color(color):
    return tuple(max(0, min(255, int(value))) for value in color)


def tint_surface(surface, color, alpha=90):
    tinted = surface.copy()
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((*_clamp_color(color), alpha))
    tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return tinted


def make_vertical_gradient(size, top_color, bottom_color):
    surface = pygame.Surface(size)
    width, height = size
    for y in range(height):
        blend = y / max(1, height - 1)
        color = (
            top_color[0] + (bottom_color[0] - top_color[0]) * blend,
            top_color[1] + (bottom_color[1] - top_color[1]) * blend,
            top_color[2] + (bottom_color[2] - top_color[2]) * blend,
        )
        pygame.draw.line(surface, _clamp_color(color), (0, y), (width, y))
    return surface.convert()


def make_grid_surface(size, cell_size, color, accent):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    width, height = size
    for x in range(0, width, cell_size):
        pygame.draw.line(surface, (*color, 120), (x, 0), (x, height))
    for y in range(0, height, cell_size):
        pygame.draw.line(surface, (*color, 120), (0, y), (width, y))
    for x in range(0, width, cell_size * 4):
        pygame.draw.line(surface, (*accent, 60), (x, 0), (x, height), 2)
    for y in range(0, height, cell_size * 4):
        pygame.draw.line(surface, (*accent, 60), (0, y), (width, y), 2)
    return surface


def make_player_surface(size):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    rect = surface.get_rect()
    pygame.draw.circle(surface, (57, 161, 255), rect.center, rect.width // 2 - 2)
    pygame.draw.circle(surface, (203, 236, 255), rect.center, rect.width // 4)
    pygame.draw.circle(surface, (255, 255, 255), (rect.centerx + 5, rect.centery - 5), 3)
    return surface


def make_enemy_surface(size, primary, secondary):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    rect = surface.get_rect()
    pygame.draw.circle(surface, primary, rect.center, rect.width // 2 - 2)
    pygame.draw.circle(surface, secondary, rect.center, rect.width // 4)
    pygame.draw.circle(surface, (255, 255, 255), (rect.centerx - 5, rect.centery - 4), 2)
    pygame.draw.circle(surface, (255, 255, 255), (rect.centerx + 5, rect.centery - 4), 2)
    return surface


def make_hostage_surface(size):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    rect = surface.get_rect()
    pygame.draw.rect(surface, (255, 214, 85), (rect.centerx - 8, 12, 16, rect.height - 20), border_radius=8)
    pygame.draw.circle(surface, (255, 236, 175), (rect.centerx, 9), 8)
    pygame.draw.rect(surface, (53, 37, 18), (rect.centerx - 6, 18, 12, 4), border_radius=2)
    return surface


def make_boss_surface(size):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    rect = surface.get_rect()
    pygame.draw.circle(surface, (194, 63, 255), rect.center, rect.width // 2 - 2)
    pygame.draw.circle(surface, (255, 130, 85), rect.center, rect.width // 4 + 4)
    pygame.draw.circle(surface, (255, 255, 255), (rect.centerx - 10, rect.centery - 10), 4)
    pygame.draw.circle(surface, (255, 255, 255), (rect.centerx + 10, rect.centery - 10), 4)
    return surface


class AssetManager:
    """Quan ly asset theo huong fallback an toan khi thieu file PNG."""

    def __init__(self):
        self.project_root = Path(config.PROJECT_ROOT)
        self.font_title = pygame.font.SysFont("bahnschrift", 64, bold=True)
        self.font_h1 = pygame.font.SysFont("segoeui", 36, bold=True)
        self.font_h2 = pygame.font.SysFont("segoeui", 24, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 20)
        self.font_small = pygame.font.SysFont("consolas", 16)

        self.menu_background = make_vertical_gradient(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
            (10, 16, 34),
            (4, 8, 16),
        )
        self.world_background = make_vertical_gradient(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
            (8, 16, 31),
            (4, 8, 14),
        )
        self.grid_overlay = make_grid_surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT),
            24,
            config.COLOR_GRID,
            config.COLOR_BORDER,
        )

        self.images = {
            "player": self.load_optional_image("player.png", (34, 34), alpha=True) or make_player_surface((34, 34)),
            "hostage": self.load_optional_image("hostage.png", (26, 42), alpha=True) or make_hostage_surface((26, 42)),
            "enemy_grunt": self.load_optional_image("enemy.png", (30, 30), alpha=True) or make_enemy_surface((30, 30), (246, 87, 110), (255, 205, 214)),
            "enemy_runner": make_enemy_surface((26, 26), (255, 169, 55), (255, 228, 175)),
            "enemy_shooter": make_enemy_surface((32, 32), (134, 94, 255), (219, 208, 255)),
            "boss": self.load_optional_image("boss.png", (96, 96), alpha=True) or make_boss_surface((96, 96)),
            "world_bg": self.load_optional_image("bg.png", (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), alpha=False),
        }

    def load_optional_image(self, filename, size, alpha=True):
        path = self.project_root / filename
        if not path.exists():
            return None

        image = pygame.image.load(str(path))
        image = image.convert_alpha() if alpha else image.convert()
        return pygame.transform.smoothscale(image, size)
