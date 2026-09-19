import sys

import pygame

from assets_loader import assets
from scene_manager import BaseScene
from settings import INTERNAL_HEIGHT, INTERNAL_WIDTH
from ui import Button, VBox


class PauseScene(BaseScene):
    def __init__(self, game_scene=None):
        super().__init__()
        self.is_overlay = True
        self.game_scene = game_scene

        # Auto Layout container for buttons
        btn_w = 90
        btn_h = 16
        self.menu_layout = VBox(
            x=INTERNAL_WIDTH // 2 - btn_w // 2,
            y=48,
            gap=3,
            align="center",
            children=[
                Button("LANJUT", width=btn_w, height=btn_h, on_click=self.resume),
                Button("MENU UTAMA", width=btn_w, height=btn_h, on_click=self.to_main_menu),
                Button("PENGATURAN", width=btn_w, height=btn_h, on_click=self.open_settings),
                Button("KELUAR", width=btn_w, height=btn_h, on_click=self.quit_app),
            ]
        )

        # Mapped Key Actions
        self.key_actions = {
            pygame.K_ESCAPE: self.resume,
            pygame.K_p: self.resume,
        }

    def resume(self):
        self.manager.pop_scene()

    def open_settings(self):
        from scenes.settings_scene import SettingsScene
        self.manager.push_scene(SettingsScene())

    def to_main_menu(self):
        if self.game_scene:
            self.game_scene.persist_save()
        from scenes.title_scene import TitleScene
        self.manager.change_scene(TitleScene())

    def quit_app(self):
        if self.game_scene:
            self.game_scene.persist_save()
        pygame.quit()
        sys.exit()

    def handle_event(self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]):
        if event.type == pygame.KEYDOWN and event.key in self.key_actions:
            self.key_actions[event.key]()
            return

        self.menu_layout.handle_event(event, mouse_canvas_pos)

    def draw(self, canvas: pygame.Surface):
        # Dark overlay
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        canvas.blit(overlay, (0, 0))

        # Pause Card Modal
        card = pygame.Rect(INTERNAL_WIDTH // 2 - 60, 26, 120, 128)
        pygame.draw.rect(canvas, (245, 240, 220), card)
        pygame.draw.rect(canvas, (120, 80, 40), card, 2)

        # Title
        title_surf = assets.render_text("GAME DIJEDA", color=(60, 40, 20))
        canvas.blit(title_surf, (card.centerx - title_surf.get_width() // 2, card.top + 8))

        # Draw Auto-Layout buttons
        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos())
        self.menu_layout.draw(canvas, mouse_pos)
