import random
import pygame

from config import (
    DAY_LENGTH_SECONDS,
    INITIAL_MONEY,
    INITIAL_REPUTATION,
    INTERNAL_HEIGHT,
    INTERNAL_WIDTH,
    REPUTATION_GAIN,
    REPUTATION_LOSS,
)
from core import BaseScene, assets, save_manager
from entities import Bowl, Customer, DraggedItem, IngredientTray, TrashCan
from items.registry import items_registry

# Environment & HUD Layout Constants
GEROBAK_SCALE = 1.0
GEROBAK_OFFSET_X = 0
GEROBAK_OFFSET_Y = 0

BOWL_HOME_POS = (780, 710)
TRASH_CAN_POS = (100, 710)
TRASH_CAN_SIZE = (160, 240)
CUSTOMER_POS = (650, 315)
CUSTOMER_SPAWN_DELAY = 1.0
ORDER_TICKET_POS = (40, 140)
ORDER_TICKET_SIZE = (280, 260)
HUD_HEIGHT = 68
PAUSE_BTN_POS = (1830, 8)
PAUSE_BTN_SIZE = (76, 52)

COLOR_BG_CYAN = (75, 205, 240)
COLOR_WHITE = (255, 255, 255)
COLOR_GOLD = (255, 205, 45)

# ==============================================================================
# FOOD STATIONS & INGREDIENTS LAYOUT
# All positions (x, y), scales, display sprites, and pickable states are tweaked here!
# ==============================================================================
FOOD_STATIONS_LAYOUT = [
    # 1. Main Pickable Ingredient Clusters (Right side of Gerobak)
    {
        "id": "bakso_halus",
        "display_sprite": "bakso-halus-cluster",
        "x": 1030,
        "y": 290,
        "scale": 0.70,
        "is_pickable": True,
        "label": "Bakso Halus",
    },
    {
        "id": "tahu",
        "display_sprite": "tahu-cluster",
        "x": 1350,
        "y": 320,
        "scale": 0.70,
        "is_pickable": True,
        "label": "Tahu",
    },
    {
        "id": "mi_kuning",
        "display_sprite": "mi-kuning-cluster",
        "x": 1360,
        "y": 480,
        "scale": 0.60,
        "is_pickable": True,
        "label": "Mie Kuning",
    },
    {
        "id": "mi_bihun",
        "display_sprite": "mi-bihun-cluster",
        "x": 1510,
        "y": 480,
        "scale": 0.60,
        "is_pickable": True,
        "label": "Bihun",
    },
    {
        "id": "gorengan_panjang",
        "display_sprite": "gorengan-panjang-cluster",
        "x": 1035,
        "y": 460,
        "scale": 0.70,
        "is_pickable": True,
        "label": "Gorengan",
    },

    # 2. Static Condiments & Sauces (Pickable bottles that disappear from shelf when dragged)
    {
        "id": "kecap",
        "display_sprite": "kecap-bottle",
        "x": 1410,
        "y": 540,
        "scale": 0.70,
        "is_pickable": True,
        "hide_on_drag": True,
        "label": "Kecap Manis",
    },
    {
        "id": "saos_sambal",
        "display_sprite": "saos-sambal-bottle",
        "x": 1540,
        "y": 555,
        "scale": 0.70,
        "is_pickable": True,
        "hide_on_drag": True,
        "label": "Saos Sambal",
    },
    {
        "id": "saos_tomat",
        "display_sprite": "saos-tomat-bottle",
        "x": 1670,
        "y": 550,
        "scale": 0.70,
        "is_pickable": True,
        "hide_on_drag": True,
        "label": "Saos Tomat",
    },

    # 3. Static Toppings & Pot
    {
        "id": "bawang_goreng",
        "display_sprite": "bawang-goreng-cluster",
        "x": 1215,
        "y": 695,
        "scale": 0.65,
        "is_pickable": True,
        "label": "Bawang Goreng",
    },
    {
        "id": "daun_bawang",
        "display_sprite": "daun-bawang-cluster",
        "x": 1040,
        "y": 700,
        "scale": 0.65,
        "is_pickable": True,
        "label": "Daun Bawang",
    },
    {
        "id": "kuah",
        "display_sprite": "kuah",
        "x": 240,
        "y": 490,
        "scale": 0.67,
        "is_pickable": False,
        "label": "Kuah Kaldu",
    },
    {
        "id": "kentongan",
        "display_sprite": "kentongan",
        "x": 1720,
        "y": 40,
        "scale": 0.65,
        "is_pickable": False,
        "label": "Kentongan",
    },
]


class GameScene(BaseScene):
    def __init__(self, save_data: dict = None):
        super().__init__()
        if save_data:
            self.day = save_data.get("day", 1)
            self.money = save_data.get("money", INITIAL_MONEY)
            self.reputation = save_data.get("reputation", INITIAL_REPUTATION)
        else:
            self.day = 1
            self.money = INITIAL_MONEY
            self.reputation = INITIAL_REPUTATION
            self.persist_save()

        self.state = "PLAYING"
        self.day_timer = DAY_LENGTH_SECONDS
        self.is_time_paused = False  # Debug pause time toggle (F4)

        self.day_earnings = 0
        self.customers_served = 0
        self.customers_failed = 0
        self.floating_texts: list[dict] = []

        # Cached scaled gerobak & background
        self.cached_gerobak: pygame.Surface | None = None
        self.cached_bg: pygame.Surface | None = None

        # Entities
        self.bowl = Bowl(x=BOWL_HOME_POS[0], y=BOWL_HOME_POS[1])
        self.trash_can = TrashCan(
            x=TRASH_CAN_POS[0],
            y=TRASH_CAN_POS[1],
        )

        # Build Trays from FOOD_STATIONS_LAYOUT
        self.trays: list[IngredientTray] = []
        for cfg in FOOD_STATIONS_LAYOUT:
            on_click = None
            if cfg["id"] == "kentongan":
                on_click = lambda: assets.play_sound("bakso.mp3", volume=1.0)

            tray = IngredientTray(
                x=cfg["x"],
                y=cfg["y"],
                item_id=cfg["id"],
                display_sprite_id=cfg.get("display_sprite"),
                is_pickable=cfg.get("is_pickable", True),
                hide_on_drag=cfg.get("hide_on_drag", False),
                scale=cfg.get("scale", 1.0),
                width=cfg.get("width"),
                height=cfg.get("height"),
                label=cfg.get("label"),
                on_click=on_click,
            )
            self.trays.append(tray)

        self.current_customer: Customer | None = Customer(x=CUSTOMER_POS[0], y=CUSTOMER_POS[1])
        self.customer_spawn_timer = 0.0

        # UI & Buttons
        self.dragged_item: DraggedItem | None = None
        self.pause_btn_rect = pygame.Rect(
            PAUSE_BTN_POS[0], PAUSE_BTN_POS[1], PAUSE_BTN_SIZE[0], PAUSE_BTN_SIZE[1]
        )
        self.next_day_btn_rect = pygame.Rect(INTERNAL_WIDTH // 2 - 140, 680, 280, 72)
        self.restart_btn_rect = pygame.Rect(INTERNAL_WIDTH // 2 - 140, 640, 280, 72)
        self.pause_btn_hovered = False
        self.next_day_hovered = False
        self.restart_hovered = False

        # Mapped Key Actions (Pause menu, Serve, Clear, F4 debug time pause)
        self.key_actions = {
            pygame.K_ESCAPE: self.open_pause_menu,
            pygame.K_p: self.open_pause_menu,
            pygame.K_SPACE: self.serve_current_bowl,
            pygame.K_RETURN: self.serve_current_bowl,
            pygame.K_c: self.bowl.clear,
            pygame.K_BACKSPACE: self.bowl.clear,
            pygame.K_F4: self.toggle_debug_pause_time,
        }

    def toggle_debug_pause_time(self):
        self.is_time_paused = not self.is_time_paused
        status_str = "DIJEDA (PAUSED)" if self.is_time_paused else "BERJALAN (RESUMED)"
        self.add_floating_text(
            f"WAKTU {status_str}",
            INTERNAL_WIDTH // 2,
            120,
            (255, 230, 80) if self.is_time_paused else (100, 255, 120),
        )

    def add_floating_text(
        self, text: str, x: int, y: int, color: tuple[int, int, int]
    ):
        self.floating_texts.append({
            "text": text,
            "x": float(x),
            "y": float(y),
            "vy": -40.0,
            "color": color,
            "lifetime": 1.4,
            "max_life": 1.4,
        })

    def persist_save(self):
        save_manager.save_game({
            "day": self.day,
            "money": self.money,
            "reputation": self.reputation,
        })

    def handle_event(
        self, event: pygame.event.Event, mouse_canvas_pos: tuple[int, int]
    ):
        if event.type == pygame.KEYDOWN and event.key in self.key_actions:
            self.key_actions[event.key]()
            return

        if self.state == "PLAYING":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.pause_btn_rect.collidepoint(mouse_canvas_pos):
                    assets.play_sound("click2.ogg", volume=1)
                    self.open_pause_menu()
                    return

                tray_clicked = False
                for tray in self.trays:
                    drag = tray.handle_mouse_down(mouse_canvas_pos)
                    if drag:
                        self.dragged_item = drag
                        tray_clicked = True
                        break

                if not tray_clicked and self.bowl.contains_point(
                    mouse_canvas_pos
                ):
                    self.bowl.start_drag(mouse_canvas_pos)

            elif event.type == pygame.MOUSEMOTION:
                if self.dragged_item:
                    self.dragged_item.update(mouse_canvas_pos)

                if self.bowl.is_dragging:
                    self.bowl.update_drag(mouse_canvas_pos)
                    bowl_center = (
                        self.bowl.x + self.bowl.width // 2,
                        self.bowl.y + self.bowl.height // 2,
                    )
                    self.trash_can.is_hovered = (
                        self.trash_can.contains_point(bowl_center)
                        or self.trash_can.contains_point(mouse_canvas_pos)
                    )
                else:
                    self.trash_can.is_hovered = False

                for tray in self.trays:
                    tray.update_hover(mouse_canvas_pos)

                self.bowl.update_hover(mouse_canvas_pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragged_item:
                    source = self.dragged_item.source_tray
                    if self.bowl.contains_point(mouse_canvas_pos):
                        self.bowl.add_ingredient(
                            self.dragged_item.item_id,
                            drop_pos=mouse_canvas_pos,
                        )
                    if source:
                        source.is_held = False
                    self.dragged_item = None

                if self.bowl.is_dragging:
                    bowl_center = (
                        self.bowl.x + self.bowl.width // 2,
                        self.bowl.y + self.bowl.height // 2,
                    )

                    if (
                        self.trash_can.contains_point(bowl_center)
                        or self.trash_can.contains_point(mouse_canvas_pos)
                    ):
                        self.bowl.clear()
                        self.bowl.reset_position()
                    elif (
                        self.current_customer
                        and self.current_customer.contains_point(bowl_center)
                    ):
                        self.serve_current_bowl()
                        self.bowl.reset_position()
                    else:
                        self.bowl.place_on_counter()

                    self.trash_can.is_hovered = False

        elif self.state == "DAY_SUMMARY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.next_day_btn_rect.collidepoint(mouse_canvas_pos):
                    assets.play_sound("click2.ogg", volume=1)
                    self.start_next_day()

        elif self.state == "GAME_OVER":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.restart_btn_rect.collidepoint(mouse_canvas_pos):
                    assets.play_sound("click2.ogg", volume=1)
                    self.restart_game()

    def open_pause_menu(self):
        from scenes.pause_scene import PauseScene

        if self.dragged_item and self.dragged_item.source_tray:
            self.dragged_item.source_tray.is_held = False
        self.dragged_item = None
        self.bowl.reset_position()
        self.trash_can.is_hovered = False
        self.manager.push_scene(PauseScene(game_scene=self))

    def serve_current_bowl(self):
        if not self.current_customer or self.current_customer.state != "waiting":
            return

        bowl_contents = self.bowl.get_ingredient_counts()
        is_correct, earned = self.current_customer.serve(bowl_contents)

        if is_correct:
            self.money += earned
            self.day_earnings += earned
            self.reputation = min(100, self.reputation + REPUTATION_GAIN)
            self.customers_served += 1
            self.add_floating_text(
                f"+Rp {earned:,}",
                self.current_customer.x,
                self.current_customer.y - 40,
                (80, 240, 100),
            )
        else:
            self.reputation = max(0, self.reputation - REPUTATION_LOSS)
            self.customers_failed += 1
            self.add_floating_text(
                "+Rp 0",
                self.current_customer.x,
                self.current_customer.y - 40,
                (255, 80, 80),
            )
            if self.reputation <= 0:
                self.state = "GAME_OVER"
                save_manager.delete_save()

        self.bowl.clear()

    def update(self, dt: float):
        for ft in self.floating_texts:
            ft["lifetime"] -= dt
            ft["y"] += ft["vy"] * dt
        self.floating_texts = [
            ft for ft in self.floating_texts if ft["lifetime"] > 0
        ]

        if self.state == "PLAYING":
            # If debug pause time is enabled, freeze clock, customer timers & spawning
            if not self.is_time_paused:
                self.day_timer -= dt
                if self.day_timer <= 0:
                    self.day_timer = 0
                    self.state = "DAY_SUMMARY"
                    self.persist_save()
                    return

                if self.current_customer:
                    self.current_customer.update(dt)
                    if (
                        self.current_customer.state == "angry"
                        and self.current_customer.patience == 0
                        and self.current_customer.feedback_timer >= 1.95
                    ):
                        self.reputation = max(0, self.reputation - REPUTATION_LOSS)
                        self.customers_failed += 1
                        self.add_floating_text(
                            "Order canceled",
                            self.current_customer.x,
                            self.current_customer.y - 40,
                            (255, 80, 80),
                        )
                        if self.reputation <= 0:
                            self.state = "GAME_OVER"
                            save_manager.delete_save()
                            return

                    if self.current_customer.state == "done":
                        self.current_customer = None
                        self.customer_spawn_timer = CUSTOMER_SPAWN_DELAY
                else:
                    self.customer_spawn_timer -= dt
                    if self.customer_spawn_timer <= 0:
                        self.current_customer = Customer(x=CUSTOMER_POS[0], y=CUSTOMER_POS[1])

    def start_next_day(self):
        self.day += 1
        self.day_timer = DAY_LENGTH_SECONDS
        self.day_earnings = 0
        self.customers_served = 0
        self.customers_failed = 0
        self.floating_texts.clear()
        self.current_customer = Customer(x=CUSTOMER_POS[0], y=CUSTOMER_POS[1])
        self.bowl.clear()
        self.bowl.reset_position()
        if self.dragged_item and self.dragged_item.source_tray:
            self.dragged_item.source_tray.is_held = False
        self.dragged_item = None
        self.persist_save()
        self.state = "PLAYING"

    def restart_game(self):
        self.day = 1
        self.money = INITIAL_MONEY
        self.reputation = INITIAL_REPUTATION
        self.start_next_day()

    def draw_environment(self, canvas: pygame.Surface):
        # 1. Background image (assets/sprites/game/background.jpg)
        bg_spr = assets.get_sprite("background")
        if bg_spr:
            if self.cached_bg is None:
                bw, bh = bg_spr.get_size()
                scale = max(INTERNAL_WIDTH / bw, INTERNAL_HEIGHT / bh)
                rw, rh = int(bw * scale), int(bh * scale)
                self.cached_bg = pygame.transform.smoothscale(bg_spr, (rw, rh))
            canvas.blit(
                self.cached_bg,
                ((INTERNAL_WIDTH - self.cached_bg.get_width()) // 2, 0),
            )
            # 10% Dim overlay
            dim_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
            dim_surf.fill((0, 0, 0, 26))
            canvas.blit(dim_surf, (0, 0))
        else:
            canvas.fill(COLOR_BG_CYAN)

        # 2. Main Gerobak view (Seller POV)
        gerobak_spr = assets.get_sprite("gerobak") or assets.get_sprite("main")
        if gerobak_spr:
            if self.cached_gerobak is None:
                gw, gh = gerobak_spr.get_size()
                scale = max(INTERNAL_WIDTH / gw, INTERNAL_HEIGHT / gh) * GEROBAK_SCALE
                rw, rh = int(gw * scale), int(gh * scale)
                self.cached_gerobak = pygame.transform.smoothscale(gerobak_spr, (rw, rh))

            gx = (INTERNAL_WIDTH - self.cached_gerobak.get_width()) // 2 + GEROBAK_OFFSET_X
            gy = (INTERNAL_HEIGHT - self.cached_gerobak.get_height()) // 2 + GEROBAK_OFFSET_Y
            canvas.blit(self.cached_gerobak, (gx, gy))

    def _draw_reputation_face(self, canvas: pygame.Surface, cx: int, cy: int):
        if self.reputation >= 80:
            face_bg = (70, 210, 90)
            mood = "😄"
        elif self.reputation >= 60:
            face_bg = (150, 215, 70)
            mood = "🙂"
        elif self.reputation >= 35:
            face_bg = (245, 195, 60)
            mood = "😐"
        elif self.reputation >= 15:
            face_bg = (245, 130, 50)
            mood = "🙁"
        else:
            face_bg = (240, 70, 70)
            mood = "😡"

        pygame.draw.circle(canvas, face_bg, (cx, cy), 18)
        pygame.draw.circle(canvas, (40, 30, 20), (cx, cy), 18, 2)

        rep_txt = assets.render_text(mood, size=20, color=(30, 20, 10))
        canvas.blit(rep_txt, (cx - rep_txt.get_width() // 2, cy - rep_txt.get_height() // 2))

    def draw_hud(self, canvas: pygame.Surface):
        # Top bar container
        hud_bar = pygame.Surface((INTERNAL_WIDTH, HUD_HEIGHT), pygame.SRCALPHA)
        hud_bar.fill((35, 25, 20, 220))
        pygame.draw.line(hud_bar, COLOR_GOLD, (0, HUD_HEIGHT - 1), (INTERNAL_WIDTH, HUD_HEIGHT - 1), 3)
        canvas.blit(hud_bar, (0, 0))

        # Clock calculation (10:00 to 20:00)
        elapsed_seconds = DAY_LENGTH_SECONDS - self.day_timer
        elapsed_minutes = int(elapsed_seconds)
        current_total_minutes = 10 * 60 + elapsed_minutes
        hour = min(20, current_total_minutes // 60)
        minute = current_total_minutes % 60 if hour < 20 else 0

        # Day & Time
        hud_left = f"DAY {self.day}  |  TIME: {hour:02d}:{minute:02d}"
        surf_left = assets.render_text_with_shadow(
            hud_left, size=30, color=COLOR_WHITE, shadow_color=(20, 15, 10), offset=(2, 2)
        )
        canvas.blit(surf_left, (32, 18))

        # Time Paused Debug Notice
        if self.is_time_paused:
            pause_tag = assets.render_text_with_shadow(
                "[DEBUG: TIME PAUSED (F4)]",
                size=22,
                color=(255, 220, 60),
                shadow_color=(40, 20, 10),
                offset=(1, 2),
            )
            canvas.blit(pause_tag, (32 + surf_left.get_width() + 24, 21))

        # Money
        money_str = f"Income: Rp{self.money:,}"
        surf_money = assets.render_text_with_shadow(
            money_str, size=30, color=COLOR_GOLD, shadow_color=(40, 25, 10), offset=(2, 2)
        )
        money_x = INTERNAL_WIDTH // 2 - surf_money.get_width() // 2
        canvas.blit(surf_money, (money_x, 17))

        # Reputation Face
        rep_label = assets.render_text("REPUTATION:", size=30, color=(220, 220, 220))
        rep_cx = INTERNAL_WIDTH - 160
        canvas.blit(rep_label, (rep_cx - rep_label.get_width() - 32, 20))
        self._draw_reputation_face(canvas, rep_cx, 34)

        # Pause button (using button texture)
        mouse_pos = (
            self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos())
            if (self.manager and hasattr(self.manager, "app") and self.manager.app)
            else (0, 0)
        )
        is_hover_pause = self.pause_btn_rect.collidepoint(mouse_pos)
        if is_hover_pause and not self.pause_btn_hovered:
            assets.play_sound("click1.ogg", volume=0.3)
        self.pause_btn_hovered = is_hover_pause

        pause_btn_surf = assets.get_9slice_surface(
            "button", self.pause_btn_rect.width, self.pause_btn_rect.height, slice_margin=20
        )
        canvas.blit(pause_btn_surf, self.pause_btn_rect.topleft)
        if is_hover_pause:
            pygame.draw.rect(
                canvas,
                (255, 255, 255),
                self.pause_btn_rect.inflate(4, 4),
                width=3,
                border_radius=12,
            )

        txt_pause = assets.render_text("||", size=24, color=(0, 0, 0))
        canvas.blit(
            txt_pause,
            (
                self.pause_btn_rect.centerx - txt_pause.get_width() // 2,
                self.pause_btn_rect.centery - txt_pause.get_height() // 2,
            ),
        )

    def draw_debug_hitboxes(self, canvas: pygame.Surface):
        overlay = pygame.Surface(
            (INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA
        )

        for tray in self.trays:
            pygame.draw.rect(overlay, (0, 220, 255, 60), tray.rect)
            pygame.draw.rect(overlay, (0, 240, 255, 220), tray.rect, 2)
            lbl = assets.render_text(f"[{tray.label}]", size=20, color=(0, 240, 255))
            overlay.blit(
                lbl,
                (tray.rect.centerx - lbl.get_width() // 2, tray.rect.y - 24),
            )

        bowl_hitbox = self.bowl.rect.inflate(20, 20)
        pygame.draw.rect(overlay, (255, 230, 0, 60), bowl_hitbox)
        pygame.draw.rect(overlay, (255, 240, 0, 220), bowl_hitbox, 3)
        b_lbl = assets.render_text("[Bowl Hitbox]", size=24, color=(255, 240, 0))
        overlay.blit(b_lbl, (bowl_hitbox.x, bowl_hitbox.y - 28))

        trash_dropzone = self.trash_can.rect.inflate(20, 20)
        pygame.draw.rect(overlay, (255, 50, 100, 60), trash_dropzone)
        pygame.draw.rect(overlay, (255, 50, 100, 220), trash_dropzone, 3)
        t_lbl = assets.render_text("[Trash Dropzone]", size=24, color=(255, 80, 120))
        overlay.blit(t_lbl, (trash_dropzone.x, trash_dropzone.y - 28))

        if self.current_customer:
            cust_dropzone = pygame.Rect(
                self.current_customer.x - 140, self.current_customer.y - 120, 280, 280
            )
            pygame.draw.rect(overlay, (50, 255, 80, 50), cust_dropzone)
            pygame.draw.rect(overlay, (50, 255, 80, 220), cust_dropzone, 3)
            c_lbl = assets.render_text(
                "[Customer Serve Dropzone]", size=24, color=(60, 255, 90)
            )
            overlay.blit(
                c_lbl,
                (
                    cust_dropzone.centerx - c_lbl.get_width() // 2,
                    cust_dropzone.y - 28,
                ),
            )

        dbg_tag = assets.render_text(
            "[DEBUG: F3 = Bounds | F4 = Pause Time]", size=24, color=(0, 255, 255)
        )
        overlay.blit(dbg_tag, (20, INTERNAL_HEIGHT - 36))

        canvas.blit(overlay, (0, 0))

    def draw_summary_overlay(self, canvas: pygame.Surface):
        overlay = pygame.Surface(
            (INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 190))
        canvas.blit(overlay, (0, 0))

        card = pygame.Rect(INTERNAL_WIDTH // 2 - 340, 240, 680, 540)
        bg_surf = assets.get_9slice_surface("ui-background", card.width, card.height, slice_margin=32)
        canvas.blit(bg_surf, card.topleft)

        title = assets.render_text(
            f"DAY {self.day} FINISHED!", size=42, color=(255, 255, 255)
        )
        canvas.blit(
            title, (card.centerx - title.get_width() // 2, card.top + 40)
        )

        y = card.top + 115
        line1 = assets.render_text(
            f"Pesanan Berhasil : {self.customers_served}", size=30, color=(255, 255, 255)
        )
        line2 = assets.render_text(
            f"Pesanan Gagal/Kabur : {self.customers_failed}",
            size=30,
            color=(255, 255, 255),
        )
        line3 = assets.render_text(
            f"Total Income : Rp {self.money:,}", size=32, color=(255, 255, 255)
        )

        canvas.blit(line1, (card.left + 56, y))
        canvas.blit(line2, (card.left + 56, y + 54))
        canvas.blit(line3, (card.left + 56, y + 108))

        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos())
        is_hover = self.next_day_btn_rect.collidepoint(mouse_pos)
        if is_hover and not self.next_day_hovered:
            assets.play_sound("click1.ogg", volume=0.3)
        self.next_day_hovered = is_hover

        btn_surf = assets.get_9slice_surface("button", self.next_day_btn_rect.width, self.next_day_btn_rect.height)
        canvas.blit(btn_surf, self.next_day_btn_rect.topleft)
        if is_hover:
            pygame.draw.rect(
                canvas,
                (255, 255, 255),
                self.next_day_btn_rect.inflate(6, 6),
                width=4,
                border_radius=16,
            )

        btn_txt = assets.render_text("NEXT DAY", size=30, color=(0, 0, 0))
        canvas.blit(
            btn_txt,
            (
                self.next_day_btn_rect.centerx - btn_txt.get_width() // 2,
                self.next_day_btn_rect.centery - btn_txt.get_height() // 2,
            ),
        )

    def draw_game_over(self, canvas: pygame.Surface):
        overlay = pygame.Surface(
            (INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((40, 10, 10, 220))
        canvas.blit(overlay, (0, 0))

        card = pygame.Rect(INTERNAL_WIDTH // 2 - 320, 320, 640, 480)
        bg_surf = assets.get_9slice_surface("ui-background", card.width, card.height, slice_margin=32)
        canvas.blit(bg_surf, card.topleft)

        title = assets.render_text("GAME OVER!", size=50, color=(255, 255, 255))
        canvas.blit(
            title, (card.centerx - title.get_width() // 2, card.top + 40)
        )

        msg = assets.render_text(
            "Your reputation is 0%", size=30, color=(255, 255, 255)
        )
        canvas.blit(msg, (card.centerx - msg.get_width() // 2, card.top + 120))

        mouse_pos = self.manager.app.window_to_canvas_pos(pygame.mouse.get_pos())
        is_hover = self.restart_btn_rect.collidepoint(mouse_pos)
        if is_hover and not self.restart_hovered:
            assets.play_sound("click1.ogg", volume=0.3)
        self.restart_hovered = is_hover

        btn_surf = assets.get_9slice_surface("button", self.restart_btn_rect.width, self.restart_btn_rect.height)
        canvas.blit(btn_surf, self.restart_btn_rect.topleft)
        if is_hover:
            pygame.draw.rect(
                canvas,
                (255, 255, 255),
                self.restart_btn_rect.inflate(6, 6),
                width=4,
                border_radius=16,
            )

        btn_txt = assets.render_text("TRY AGAIN", size=30, color=(0, 0, 0))
        canvas.blit(
            btn_txt,
            (
                self.restart_btn_rect.centerx - btn_txt.get_width() // 2,
                self.restart_btn_rect.centery - btn_txt.get_height() // 2,
            ),
        )

    def draw(self, canvas: pygame.Surface):
        self.draw_environment(canvas)

        if self.current_customer:
            self.current_customer.draw(canvas)
            if self.current_customer.state == "waiting":
                self.current_customer.order.draw_ticket(
                    canvas,
                    x=ORDER_TICKET_POS[0],
                    y=ORDER_TICKET_POS[1],
                    width=ORDER_TICKET_SIZE[0],
                    height=ORDER_TICKET_SIZE[1],
                )

        # 1. Background trays & food stations (including kuah pot)
        for tray in self.trays:
            tray.draw(canvas)

        # 2. Trash can in front of kuah
        self.trash_can.draw(canvas)

        # 3. Main bowl and dragged items in front of trash can
        self.bowl.draw(canvas)

        if self.dragged_item:
            self.dragged_item.draw(canvas)

        for ft in self.floating_texts:
            alpha_ratio = min(1.0, ft["lifetime"] / (ft["max_life"] * 0.4))
            surf = assets.render_text_with_shadow(
                ft["text"], size=32, color=ft["color"], shadow_color=(10, 10, 10), offset=(2, 2)
            )
            if alpha_ratio < 1.0:
                surf.set_alpha(int(255 * alpha_ratio))
            canvas.blit(
                surf, (int(ft["x"]) - surf.get_width() // 2, int(ft["y"]))
            )

        if (
            self.manager
            and hasattr(self.manager, "app")
            and getattr(self.manager.app, "show_hitboxes", False)
        ):
            self.draw_debug_hitboxes(canvas)

        self.draw_hud(canvas)

        if self.state == "DAY_SUMMARY":
            self.draw_summary_overlay(canvas)
        elif self.state == "GAME_OVER":
            self.draw_game_over(canvas)
