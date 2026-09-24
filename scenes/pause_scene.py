import sys

import pygame

from config import INTERNAL_HEIGHT, INTERNAL_WIDTH
from core import BaseScene
from ui import Button, Label, PanelContainer, VBoxContainer


class PauseScene(BaseScene):
    def __init__(self, game_scene=None):
        super().__init__()
        self.is_overlay = True
        self.game_scene = game_scene

        btn_w = 260
        btn_h = 60
        btn_font = 26

        self.panel = PanelContainer(
            padding=(36, 44, 36, 44),
            use_texture=True,
            texture_id="ui-background",
            slice_margin=32,
            children=[
                VBoxContainer(
                    separation=16,
                    align_items="center",
                    children=[
                        Label(
                            "GAME PAUSED",
                            font_size=40,
                            color=(255, 255, 255),
                            margin=(0, 0, 10, 0),
                        ),
                        Button(
                            "RESUME",
                            width=btn_w,
                            height=btn_h,
                            font_size=btn_font,
                            on_click=self.resume,
                        ),
                        Button(
                            "SETTINGS",
                            width=btn_w,
                            height=btn_h,
                            font_size=btn_font,
                            on_click=self.open_settings,
                        ),
                        Button(
                            "MAIN MENU",
                            width=btn_w,
                            height=btn_h,
                            font_size=btn_font,
                            on_click=self.to_main_menu,
                        ),
                        Button(
                            "EXIT GAME",
                            width=btn_w,
                            height=btn_h,
                            font_size=btn_font,
                            on_click=self.quit_app,
                        ),
                    ],
                )
            ],
        )
        pw, ph = self.panel.get_minimum_size()
        self.panel.rect.topleft = (
            INTERNAL_WIDTH // 2 - pw // 2,
            INTERNAL_HEIGHT // 2 - ph // 2,
        )
        self.panel.reflow()

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

    def handle_event(
        self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]
    ):
        if event.type == pygame.KEYDOWN and event.key in self.key_actions:
            self.key_actions[event.key]()
            return

        self.panel.handle_event(event, mouse_canvas_pos)

    def draw(self, canvas: pygame.Surface):
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        canvas.blit(overlay, (0, 0))

        mouse_pos = (
            self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos())
            if (self.manager and hasattr(self.manager, "app") and self.manager.app)
            else (0, 0)
        )
        self.panel.draw(canvas, mouse_pos)
