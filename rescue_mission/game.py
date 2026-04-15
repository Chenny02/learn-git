"""Game bootstrap và state machine tổng.

Ý tưởng kiến trúc:
- `Game` chỉ điều phối trạng thái lớn của ứng dụng.
- Toàn bộ logic chiến đấu của 1 màn được giao cho `LevelScene`.
- UI được gọi từ đây, nhưng `Game` không tự vẽ chi tiết từng entity.

Nhờ cách tách này, ta có thể thay đổi gameplay từng màn mà không phải sửa menu,
và cũng có thể đổi giao diện mà không làm vỡ combat loop.
"""

import sys

import pygame

from . import config, ui
from .assets import AssetManager
from .level_system import LevelScene, build_level_specs
from .states import GameState


class Game:
    """State machine tổng cho menu, chơi game, qua màn, thua và chiến thắng."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.TITLE)
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.assets = AssetManager()
        self.level_specs = build_level_specs()
        self.buttons = [
            ui.Button(pygame.Rect(70, 420, 300, 82), "Bắt đầu", "Chơi ngay"),
            ui.Button(pygame.Rect(70, 520, 300, 82), "Thoát", "Rời game"),
        ]

        pygame.mouse.set_visible(False)

        self.running = True
        self.state = GameState.MENU
        self.level_index = 0
        self.scene = None
        self.total_score = 0
        self.overlay_timer = 0
        self.menu_pulse = 0

    def run(self):
        """Vòng lặp chính của game.

        Mỗi frame chỉ làm 3 việc:
        1. Đọc input
        2. Update state hiện tại
        3. Vẽ state hiện tại
        """

        while self.running:
            self.clock.tick(config.FPS)
            self.menu_pulse += 1
            self.handle_events()
            self.update()
            self.draw()

        pygame.mouse.set_visible(True)
        pygame.quit()

    def handle_events(self):
        """Phân input theo state để tránh if/else lớn trong mỗi scene."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.state == GameState.MENU:
                self.handle_menu_event(event)
            elif self.state == GameState.PLAYING:
                self.handle_playing_event(event)
            else:
                self.handle_overlay_event(event)

    def handle_menu_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        mouse_pos = pygame.mouse.get_pos()
        if self.buttons[0].hovered(mouse_pos):
            self.start_new_campaign()
        elif self.buttons[1].hovered(mouse_pos):
            self.running = False

    def handle_playing_event(self, event):
        # ESC được giữ lại như một nút thoát nhanh về menu.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.return_to_menu()

    def handle_overlay_event(self, event):
        # Sau màn hoặc khi thua, bất kỳ phím/chuột đều là một xác nhận hợp lý.
        if event.type not in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            return

        if self.state == GameState.LEVEL_COMPLETE:
            self.begin_next_level()
        else:
            self.return_to_menu()

    def update(self):
        """Chỉ cập nhật state hiện tại; Game không chen vào nội bộ combat."""

        if self.state == GameState.PLAYING:
            self.scene.update()

            if self.scene.result == "win":
                self.total_score += self.scene.score
                if self.level_index == len(self.level_specs) - 1:
                    self.state = GameState.VICTORY
                else:
                    self.state = GameState.LEVEL_COMPLETE
                self.overlay_timer = config.LEVEL_COMPLETE_DELAY

            elif self.scene.result == "lose":
                self.total_score += self.scene.score
                self.state = GameState.GAME_OVER

        elif self.state == GameState.LEVEL_COMPLETE and self.overlay_timer > 0:
            self.overlay_timer -= self.clock.get_time()
            if self.overlay_timer <= 0:
                self.begin_next_level()

    def draw(self):
        """Mỗi state có cách vẽ riêng, nhưng đều đi qua một điểm trung tâm."""

        if self.state == GameState.MENU:
            ui.draw_menu(
                self.screen,
                self.assets,
                self.buttons,
                pygame.mouse.get_pos(),
                self.total_score,
                self.menu_pulse,
            )

        elif self.state == GameState.PLAYING:
            self.scene.draw(self.screen)
            ui.draw_hud(self.screen, self.assets, self.scene, self.describe_next_upgrade())

        elif self.state == GameState.LEVEL_COMPLETE:
            self.scene.draw(self.screen)
            ui.draw_hud(self.screen, self.assets, self.scene, self.describe_next_upgrade())
            ui.draw_overlay(
                self.screen,
                self.assets,
                "HOÀN THÀNH",
                self.scene.result_reason,
                "Nhấn phím bất kỳ để qua màn.",
                config.COLOR_ACCENT,
            )

        elif self.state == GameState.GAME_OVER:
            self.scene.draw(self.screen)
            ui.draw_hud(self.screen, self.assets, self.scene, self.describe_next_upgrade())
            ui.draw_overlay(
                self.screen,
                self.assets,
                "THẤT BẠI",
                self.scene.result_reason,
                "Nhấn phím bất kỳ để về menu.",
                config.COLOR_DANGER,
            )

        elif self.state == GameState.VICTORY:
            self.scene.draw(self.screen)
            ui.draw_hud(self.screen, self.assets, self.scene, "Chiến dịch đã hoàn tất.")
            ui.draw_overlay(
                self.screen,
                self.assets,
                "CHIẾN THẮNG",
                "Orion đã bị hạ. Con tin an toàn.",
                f"Tổng điểm: {self.total_score}",
                config.COLOR_WARNING,
            )

        pygame.display.flip()

    def start_new_campaign(self):
        """Reset campaign và tạo scene cho màn đầu tiên."""

        self.total_score = 0
        self.level_index = 0
        self.scene = LevelScene(self.assets, self.level_specs[self.level_index])
        self.state = GameState.PLAYING

    def begin_next_level(self):
        """Chuyển sang màn tiếp theo, nếu hết màn thì vào state chiến thắng."""

        self.level_index += 1
        if self.level_index >= len(self.level_specs):
            self.state = GameState.VICTORY
            return

        self.scene = LevelScene(self.assets, self.level_specs[self.level_index])
        self.state = GameState.PLAYING

    def return_to_menu(self):
        """Xóa scene hiện tại để quay lại menu sạch sẽ."""

        self.state = GameState.MENU
        self.scene = None

    def describe_next_upgrade(self):
        """Giữ lại thông tin progression để có thể dùng lại nếu UI cần."""

        current_level = min(self.level_index + 1, len(self.level_specs))
        if self.state == GameState.VICTORY:
            return "Chiến dịch đã hoàn tất."

        next_level = min(len(self.level_specs), current_level + 1)
        if next_level == current_level:
            return "Không còn nâng cấp."

        upgrade = config.upgrade_for_level(next_level)
        return f"Mở khóa: {upgrade.title}"


def main():
    """Entrypoint chung cho file launcher."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    Game().run()
