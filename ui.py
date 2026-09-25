import math
import sys
import pygame
from main import (
    INTERNAL_HEIGHT,
    INTERNAL_WIDTH,
    BaseScene,
    assets,
    save_manager,
)

COLOR_BG_CYAN = (75, 205, 240)
COLOR_GOLD = (255, 205, 45)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)


class Button:
    def __init__(
        self,
        text: str,
        x: int = 0,
        y: int = 0,
        width: int = 240,
        height: int = 60,
        font_size: int = 26,
        on_click=None,
        use_texture: bool = True,
        texture_id: str = "button",
        bg_color: tuple[int, int, int] = (235, 150, 50),
        text_color: tuple[int, int, int] = (0, 0, 0),
        is_active: bool = False,
    ):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.font_size = font_size
        self.on_click = on_click
        self.use_texture = use_texture
        self.texture_id = texture_id
        self.bg_color = bg_color
        self.text_color = text_color
        self.is_active = is_active
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event, mouse_pos: tuple[int, int]) -> bool:
        hovered = self.rect.collidepoint(mouse_pos)
        if hovered and not self.is_hovered:
            assets.play_sound("click1.ogg", volume=0.3)
        self.is_hovered = hovered

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                assets.play_sound("click2.ogg", volume=1.0)
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int] = (0, 0)):
        hovered = self.rect.collidepoint(mouse_pos)
        if hovered and not self.is_hovered:
            assets.play_sound("click1.ogg", volume=0.3)
        self.is_hovered = hovered

        if self.use_texture and assets.get_sprite(self.texture_id):
            btn_surf = assets.get_9slice_surface(
                self.texture_id, self.rect.width, self.rect.height, slice_margin=24
            )
            surface.blit(btn_surf, self.rect.topleft)
        else:
            pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=12)

        if self.is_active:
            pygame.draw.rect(surface, (75, 225, 105), self.rect.inflate(6, 6), width=4, border_radius=16)
        elif self.is_hovered:
            pygame.draw.rect(surface, (255, 255, 255), self.rect.inflate(6, 6), width=4, border_radius=16)

        txt_surf = assets.render_text(self.text, size=self.font_size, color=self.text_color)
        tx = self.rect.centerx - txt_surf.get_width() // 2
        ty = self.rect.centery - txt_surf.get_height() // 2
        surface.blit(txt_surf, (tx, ty))


class TitleScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.time = 0.0
        self.buttons: list[Button] = []
        self.cached_bg = None
        self.cached_gerobak = None
        self.build_buttons()

    def on_enter(self):
        self.build_buttons()

    def build_buttons(self):
        self.buttons = []
        has_save = save_manager.has_save()
        btn_w, btn_h = 280, 64
        btn_x = INTERNAL_WIDTH // 2 - btn_w // 2
        start_y = 540 if has_save else 580
        gap = 80

        curr_y = start_y
        if has_save:
            self.buttons.append(Button("CONTINUE", x=btn_x, y=curr_y, width=btn_w, height=btn_h, on_click=self.continue_game))
            curr_y += gap

        self.buttons.append(Button("NEW GAME", x=btn_x, y=curr_y, width=btn_w, height=btn_h, on_click=self.new_game))
        curr_y += gap
        self.buttons.append(Button("EXIT GAME", x=btn_x, y=curr_y, width=btn_w, height=btn_h, on_click=self.quit_app))

    def continue_game(self):
        from game import GameScene
        save_data = save_manager.load_game()
        self.manager.change_scene(GameScene(save_data=save_data))

    def new_game(self):
        from game import GameScene
        self.manager.change_scene(GameScene(save_data=None))

    def quit_app(self):
        pygame.quit()
        sys.exit()

    def handle_event(self, event: pygame.event.Event, mouse_pos: tuple[int, int]):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.quit_app()
            return
        for btn in self.buttons:
            btn.handle_event(event, mouse_pos)

    def update(self, dt: float):
        self.time += dt

    def draw(self, canvas: pygame.Surface):
        bg_spr = assets.get_sprite("background")
        if bg_spr:
            if self.cached_bg is None:
                bw, bh = bg_spr.get_size()
                scale = max(INTERNAL_WIDTH / bw, INTERNAL_HEIGHT / bh)
                rw, rh = int(bw * scale), int(bh * scale)
                self.cached_bg = pygame.transform.smoothscale(bg_spr, (rw, rh))
            canvas.blit(self.cached_bg, ((INTERNAL_WIDTH - self.cached_bg.get_width()) // 2, 0))
        else:
            canvas.fill(COLOR_BG_CYAN)

        gerobak_spr = assets.get_sprite("gerobak") or assets.get_sprite("main")
        if gerobak_spr:
            if self.cached_gerobak is None:
                gw, gh = gerobak_spr.get_size()
                scale = max(INTERNAL_WIDTH / gw, INTERNAL_HEIGHT / gh)
                rw, rh = int(gw * scale), int(gh * scale)
                self.cached_gerobak = pygame.transform.smoothscale(gerobak_spr, (rw, rh))
            canvas.blit(self.cached_gerobak, ((INTERNAL_WIDTH - self.cached_gerobak.get_width()) // 2, 0))

            dim_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
            dim_surf.fill((0, 0, 0, 80))
            canvas.blit(dim_surf, (0, 0))

        title_surf = assets.render_text_with_shadow("SO BAKSO", size=64, color=COLOR_GOLD, shadow_color=(40, 25, 10), offset=(3, 4))
        canvas.blit(title_surf, (INTERNAL_WIDTH // 2 - title_surf.get_width() // 2, 60))

        sub_surf = assets.render_text_with_shadow("Bakso Kaki Lima Simulator", size=32, color=(255, 240, 220), shadow_color=(30, 20, 10), offset=(2, 2))
        canvas.blit(sub_surf, (INTERNAL_WIDTH // 2 - sub_surf.get_width() // 2, 140))

        bowl_back = assets.get_sprite("mangkok-back")
        bowl_front = assets.get_sprite("mangkok-front")
        bowl_shadow = assets.get_shadow_sprite("mangkok", alpha=80)
        bw = (bowl_back or bowl_front).get_width() if (bowl_back or bowl_front) else 400
        bowl_x = INTERNAL_WIDTH // 2 - bw // 2
        bowl_y = 200

        if bowl_shadow:
            canvas.blit(bowl_shadow, (bowl_x + 6, bowl_y + 12))
        if bowl_back:
            canvas.blit(bowl_back, (bowl_x, bowl_y))

        mie = assets.get_sprite("mi-kuning")
        bihun = assets.get_sprite("mi-bihun")
        halus = assets.get_sprite("bakso-halus")
        gorengan = assets.get_sprite("gorengan-panjang")
        if mie:
            canvas.blit(mie, (bowl_x + 60, bowl_y + 40))
        if bihun:
            canvas.blit(bihun, (bowl_x + 130, bowl_y + 45))
        if gorengan:
            canvas.blit(gorengan, (bowl_x + 200, bowl_y + 30))
        if halus:
            canvas.blit(halus, (bowl_x + 90, bowl_y + 70))
            canvas.blit(halus, (bowl_x + 170, bowl_y + 65))
        if bowl_front:
            canvas.blit(bowl_front, (bowl_x, bowl_y))

        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos()) if (self.manager and self.manager.app) else (0, 0)
        for btn in self.buttons:
            btn.draw(canvas, mouse_pos)


class PauseScene(BaseScene):
    def __init__(self, game_scene=None):
        super().__init__()
        self.is_overlay = True
        self.game_scene = game_scene

        self.panel_rect = pygame.Rect(INTERNAL_WIDTH // 2 - 200, INTERNAL_HEIGHT // 2 - 200, 400, 400)
        btn_w, btn_h = 260, 60
        btn_x = self.panel_rect.centerx - btn_w // 2
        start_y = self.panel_rect.y + 110
        gap = 80

        self.buttons = [
            Button("RESUME", x=btn_x, y=start_y, width=btn_w, height=btn_h, on_click=self.resume),
            Button("MAIN MENU", x=btn_x, y=start_y + gap, width=btn_w, height=btn_h, on_click=self.to_main_menu),
            Button("EXIT GAME", x=btn_x, y=start_y + gap * 2, width=btn_w, height=btn_h, on_click=self.quit_app),
        ]

    def resume(self):
        self.manager.pop_scene()

    def to_main_menu(self):
        if self.game_scene:
            self.game_scene.persist_save()
        self.manager.change_scene(TitleScene())

    def quit_app(self):
        if self.game_scene:
            self.game_scene.persist_save()
        pygame.quit()
        sys.exit()

    def handle_event(self, event: pygame.event.Event, mouse_pos: tuple[int, int]):
        if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_p]:
            self.resume()
            return
        for btn in self.buttons:
            btn.handle_event(event, mouse_pos)

    def draw(self, canvas: pygame.Surface):
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        canvas.blit(overlay, (0, 0))

        bg_surf = assets.get_9slice_surface("ui-background", self.panel_rect.width, self.panel_rect.height, slice_margin=32)
        canvas.blit(bg_surf, self.panel_rect.topleft)

        title = assets.render_text("GAME PAUSED", size=38, color=COLOR_WHITE)
        canvas.blit(title, (self.panel_rect.centerx - title.get_width() // 2, self.panel_rect.y + 40))

        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos()) if (self.manager and self.manager.app) else (0, 0)
        for btn in self.buttons:
            btn.draw(canvas, mouse_pos)
