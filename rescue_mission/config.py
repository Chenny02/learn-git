from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCREEN_WIDTH = 1180
SCREEN_HEIGHT = 760
FPS = 60

WORLD_LEFT = 28
WORLD_TOP = 108
WORLD_WIDTH = 1124
WORLD_HEIGHT = 620

TITLE = "Giải Cứu Con Tin: Shadow Protocol"
LEVEL_COMPLETE_DELAY = 1800

PLAYER_BASE_HEALTH = 110
PLAYER_BASE_SPEED = 4.0
PLAYER_BASE_FIRE_INTERVAL = 13
PLAYER_BASE_BULLET_SPEED = 12.5
PLAYER_BASE_BULLET_DAMAGE = 18
PLAYER_IFRAMES = 18

TILE_SIZE = 24
MAZE_WIDTH = 45
MAZE_HEIGHT = 25

BOSS_HEALTH = 420

COLOR_BG = (8, 14, 28)
COLOR_PANEL = (14, 24, 42)
COLOR_PANEL_ALT = (21, 34, 58)
COLOR_BORDER = (83, 161, 255)
COLOR_ACCENT = (69, 221, 191)
COLOR_ACCENT_DIM = (30, 132, 120)
COLOR_WARNING = (255, 174, 43)
COLOR_DANGER = (255, 82, 108)
COLOR_TEXT = (237, 244, 255)
COLOR_SUBTEXT = (164, 184, 214)
COLOR_GRID = (22, 40, 72)
COLOR_SHADOW = (2, 6, 14)
COLOR_MAZE_WALL = (46, 72, 108)
COLOR_MAZE_WALL_ALT = (28, 43, 68)


@dataclass(frozen=True)
class PlayerStats:
    move_speed: float
    fire_interval: int
    bullet_speed: float
    bullet_damage: int
    max_health: int


@dataclass(frozen=True)
class UpgradeInfo:
    title: str
    description: str


def player_stats_for_level(level_number: int) -> PlayerStats:
    return PlayerStats(
        move_speed=PLAYER_BASE_SPEED + 0.25 * (level_number - 1),
        fire_interval=max(6, PLAYER_BASE_FIRE_INTERVAL - (level_number - 1)),
        bullet_speed=PLAYER_BASE_BULLET_SPEED + 0.7 * (level_number - 1),
        bullet_damage=PLAYER_BASE_BULLET_DAMAGE + 3 * (level_number - 1),
        max_health=PLAYER_BASE_HEALTH + 10 * (level_number - 1),
    )


def upgrade_for_level(level_number: int) -> UpgradeInfo:
    upgrades = {
        1: UpgradeInfo("Trang bị I", "Di chuyển cơ bản, súng ổn định."),
        2: UpgradeInfo("Nhịp chiến đấu", "Bắn nhanh hơn, sát thương cao hơn."),
        3: UpgradeInfo("Bộ mê cung", "Cơ động tốt hơn trong hành lang hẹp."),
        4: UpgradeInfo("Tổng tấn công", "Giáp dày hơn, đạn bay nhanh hơn."),
    }
    return upgrades[level_number]
