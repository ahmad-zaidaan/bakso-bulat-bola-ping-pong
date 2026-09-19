import sys

import pygame

from assets_loader import assets
from scene_manager import SceneManager
from scenes.title_scene import TitleScene
from settings import (
    COLOR_BLACK,
    FPS,
    INTERNAL_HEIGHT,
    INTERNAL_WIDTH,
    SCALE,
    TITLE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.current_scale = SCALE
        self.is_fullscreen = False

        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        self.canvas = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        self.clock = pygame.time.Clock()

        assets.initialize()

        self.scene_manager = SceneManager(self)
        self.scene_manager.push_scene(TitleScene())

        # Global Key Actions (active in all screens)
        self.global_key_actions = {
            pygame.K_F11: self.toggle_fullscreen,
        }

    def set_scale(self, scale_val: int):
        self.current_scale = scale_val
        self.is_fullscreen = False
        new_w = INTERNAL_WIDTH * scale_val
        new_h = INTERNAL_HEIGHT * scale_val
        self.window = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            new_w = INTERNAL_WIDTH * self.current_scale
            new_h = INTERNAL_HEIGHT * self.current_scale
            self.window = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)

    def window_to_canvas_pos(self, window_pos: tuple[int, int]) -> tuple[int, int]:
        win_w, win_h = self.window.get_size()
        scale = min(win_w / INTERNAL_WIDTH, win_h / INTERNAL_HEIGHT)
        if scale <= 0:
            return 0, 0

        render_w = int(INTERNAL_WIDTH * scale)
        render_h = int(INTERNAL_HEIGHT * scale)
        offset_x = (win_w - render_w) // 2
        offset_y = (win_h - render_h) // 2

        wx, wy = window_pos
        cx = int((wx - offset_x) / scale)
        cy = int((wy - offset_y) / scale)
        return cx, cy

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key in self.global_key_actions:
                    self.global_key_actions[event.key]()

                mouse_canvas_pos = self.window_to_canvas_pos(pygame.mouse.get_pos())
                self.scene_manager.handle_event(event, mouse_canvas_pos)

            # Update
            self.scene_manager.update(dt)

            # Draw to native canvas
            self.scene_manager.draw(self.canvas)

            # Nearest neighbor render to window
            self.render_upscaled()
            pygame.display.flip()

    def render_upscaled(self):
        win_w, win_h = self.window.get_size()
        scale = min(win_w / INTERNAL_WIDTH, win_h / INTERNAL_HEIGHT)
        render_w = int(INTERNAL_WIDTH * scale)
        render_h = int(INTERNAL_HEIGHT * scale)
        offset_x = (win_w - render_w) // 2
        offset_y = (win_h - render_h) // 2

        scaled_surf = pygame.transform.scale(self.canvas, (render_w, render_h))
        self.window.fill(COLOR_BLACK)
        self.window.blit(scaled_surf, (offset_x, offset_y))

if __name__ == "__main__":
    app = App()
    app.run()
