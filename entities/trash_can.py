import pygame

from core.assets import assets

TRASH_CAN_POS = (140, 680)
TRASH_CAN_SCALE = 0.65
TRASH_CAN_DROPZONE_EXPAND = (30, 30)
COLOR_OUTLINE_HOVER = (255, 255, 255)


class TrashCan:
    def __init__(
        self,
        x: int = TRASH_CAN_POS[0],
        y: int = TRASH_CAN_POS[1],
        scale: float = TRASH_CAN_SCALE,
    ):
        self.x = x
        self.y = y
        self.scale = scale
        self.is_hovered = False

        raw_spr = assets.get_sprite("trash")
        raw_shadow = assets.get_shadow_sprite("trash", alpha=80)

        if self.scale != 1.0 and raw_spr:
            sw = int(raw_spr.get_width() * scale)
            sh = int(raw_spr.get_height() * scale)
            self.sprite = pygame.transform.smoothscale(raw_spr, (sw, sh))
            self.shadow_sprite = (
                pygame.transform.smoothscale(raw_shadow, (sw, sh))
                if raw_shadow
                else None
            )
        else:
            self.sprite = raw_spr
            self.shadow_sprite = raw_shadow

        self.width = self.sprite.get_width() if self.sprite else 200
        self.height = self.sprite.get_height() if self.sprite else 240
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def contains_point(self, pos: tuple[int, int]) -> bool:
        ew, eh = TRASH_CAN_DROPZONE_EXPAND
        return self.rect.inflate(ew, eh).collidepoint(pos)

    def draw(self, surface: pygame.Surface):
        # 1. Shadow underneath
        if self.shadow_sprite:
            surface.blit(self.shadow_sprite, (self.x + 6, self.y + 10))

        # 2. Sprite with white outline only when hovered (while dragging bowl)
        if self.is_hovered:
            out_spr, pad = assets.get_outlined_sprite(
                "trash",
                outline_color=COLOR_OUTLINE_HOVER,
                thickness=3,
                scale=self.scale,
            )
            if out_spr:
                surface.blit(out_spr, (self.x - pad, self.y - pad))
            elif self.sprite:
                surface.blit(self.sprite, (self.x, self.y))
        else:
            if self.sprite:
                surface.blit(self.sprite, (self.x, self.y))
