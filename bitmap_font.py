import json
import os
import pygame

class BitmapFont:
    def __init__(self, json_path: str = None):
        self.glyphs = {}
        self.char_widths = {}
        self.char_min_x = {}
        self.cache = {}
        self.char_height = 12
        self.default_advance = 6
        self.space_advance = 3

        if json_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_dir, "assets", "font", "bitmap", "monogram-bitmap.json")

        self.load(json_path)

    def load(self, json_path: str):
        if not os.path.exists(json_path):
            return
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for char, rows in data.items():
            self.glyphs[char] = rows

            # Compute min_x, max_x for proportional punctuation/characters
            min_x, max_x = 6, -1
            for r in rows:
                for b in range(6):
                    if (r >> b) & 1:
                        min_x = min(min_x, b)
                        max_x = max(max_x, b)

            if char == " ":
                self.char_widths[char] = self.space_advance
                self.char_min_x[char] = 0
            elif char in [".", ",", "!", ":", ";", "'", "|", "`"]:
                # Trim extra horizontal padding for thin punctuation
                w = (max_x - min_x + 1) if max_x >= 0 else 2
                self.char_widths[char] = w + 1  # 1px spacing
                self.char_min_x[char] = min_x if min_x <= 5 else 0
            else:
                self.char_widths[char] = self.default_advance
                self.char_min_x[char] = 0

    def _get_line_width(self, line: str, scale: int = 1) -> int:
        w = 0
        for ch in line:
            w += self.char_widths.get(ch, self.default_advance)
        return max(1, w * scale)

    def get_width(self, text: str, scale: int = 1) -> int:
        lines = text.split("\n")
        return max(self._get_line_width(line, scale) for line in lines)

    def get_height(self, text: str = "", scale: int = 1, line_spacing: int = 2) -> int:
        lines = text.split("\n")
        num_lines = max(1, len(lines))
        # Visual glyph baseline height is ~10px (rows 2 to 11), full height 12px
        h = (num_lines * 10) + ((num_lines - 1) * line_spacing)
        return max(1, h * scale)

    def render(self, text: str, color: tuple[int, int, int] = (255, 255, 255), scale: int = 1, line_spacing: int = 2) -> pygame.Surface:
        cache_key = (text, color, scale, line_spacing)
        if cache_key in self.cache:
            return self.cache[cache_key]

        lines = text.split("\n")
        max_w = max(self._get_line_width(line, 1) for line in lines)
        total_h = (len(lines) * 10) + ((len(lines) - 1) * line_spacing)
        total_h = max(10, total_h)

        surface = pygame.Surface((max_w, total_h), pygame.SRCALPHA)

        curr_y = 0
        for line in lines:
            curr_x = 0
            for ch in line:
                if ch == " ":
                    curr_x += self.space_advance
                    continue

                rows = self.glyphs.get(ch)
                if not rows:
                    curr_x += self.default_advance
                    continue

                min_x = self.char_min_x.get(ch, 0)
                for row_idx, row in enumerate(rows):
                    # Align rows slightly up (skip top blank row 0 and 1 so line height matches 10px nicely)
                    draw_y = curr_y + (row_idx - 2)
                    if not (0 <= draw_y < total_h):
                        continue

                    for bit in range(6):
                        if (row >> bit) & 1:
                            draw_x = curr_x + (bit - min_x)
                            if 0 <= draw_x < max_w:
                                surface.set_at((draw_x, draw_y), color)

                curr_x += self.char_widths.get(ch, self.default_advance)
            curr_y += 10 + line_spacing

        if scale > 1:
            surface = pygame.transform.scale(surface, (max_w * scale, total_h * scale))

        self.cache[cache_key] = surface
        return surface

    def render_with_shadow(
        self,
        text: str,
        color: tuple[int, int, int] = (255, 255, 255),
        shadow_color: tuple[int, int, int] = (0, 0, 0),
        offset: tuple[int, int] = (1, 1),
        scale: int = 1
    ) -> pygame.Surface:
        fg_surf = self.render(text, color, scale=1)
        bg_surf = self.render(text, shadow_color, scale=1)

        ox, oy = offset
        w = fg_surf.get_width() + abs(ox)
        h = fg_surf.get_height() + abs(oy)

        combined = pygame.Surface((w, h), pygame.SRCALPHA)
        combined.blit(bg_surf, (max(0, ox), max(0, oy)))
        combined.blit(fg_surf, (max(0, -ox), max(0, -oy)))

        if scale > 1:
            combined = pygame.transform.scale(combined, (w * scale, h * scale))
        return combined

# Global singleton bitmap font instance
bitmap_font = BitmapFont()
