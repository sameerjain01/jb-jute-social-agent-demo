"""
infographic_generator.py
------------------------
Creates a bold 1080x1080 PNG infographic — dark green brand design.
Themes rotate: ocean → earth → trees → water
"""

import logging
import os

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

W, H = 1080, 1080

C = {
    "bg":          (27,  67,  50),   # dark green canvas
    "card":        (36,  87,  65),   # slightly lighter green for cards
    "deco":        (22,  55,  41),   # darker for decorative shapes
    "stat":        (149, 213, 178),  # mint green — big number
    "white":       (255, 255, 255),
    "subtext":     (216, 243, 220),  # very light green
    "cta":         (255, 225, 104),  # warm yellow — pops on green
    "brown":       (139, 94,  60),
    "accent_line": (82,  183, 136),
}

THEME_TAGLINES = {
    "ocean": "Every plastic bag you skip is one less\nthing drowning our oceans.",
    "earth": "The earth doesn't need saving.\nIt needs fewer excuses.",
    "trees": "We plant nothing back when we\nchoose synthetic over natural.",
    "water": "Clean water isn't guaranteed.\nYour packaging choices affect it.",
}

THEME_ORDER = ["ocean", "earth", "trees", "water"]

FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _stat_size(stat: str) -> int:
    n = len(stat)
    if n <= 4:  return 140
    if n <= 6:  return 110
    return 88


class InfographicGenerator:

    def __init__(self, output_dir: str = "/tmp"):
        self.output_dir = output_dir

    def generate(self, data: dict, run_id: str) -> str:
        img  = Image.new("RGB", (W, H), C["bg"])
        draw = ImageDraw.Draw(img)

        self._decorative_bg(draw)
        self._header(draw, data)
        self._tagline(draw, data)
        self._stat_card(draw, data)
        self._bullets(draw, data)
        self._cta(draw, data)
        self._footer(draw, data)

        path = os.path.join(self.output_dir, f"{run_id}_infographic.png")
        img.save(path, "PNG")
        logger.info(f"Infographic saved: {path}")
        return path

    # ------------------------------------------------------------------ #

    def _decorative_bg(self, draw):
        # Large circle top-right
        draw.ellipse([(700, -180), (1180, 300)], fill=C["deco"])
        # Small circle bottom-left
        draw.ellipse([(-100, 820), (200, 1120)], fill=C["deco"])
        # Horizontal accent stripe
        draw.rectangle([(0, 148), (W, 152)], fill=C["accent_line"])

    def _header(self, draw, data):
        draw.text((50, 44), "JuteVerde", font=_font(FONT_BOLD, 58), fill=C["white"])
        theme = data.get("theme", "earth").upper()
        f = _font(FONT_REGULAR, 26)
        bbox = draw.textbbox((0, 0), theme, font=f)
        draw.text((W - (bbox[2]-bbox[0]) - 50, 60), theme, font=f, fill=C["stat"])

    def _tagline(self, draw, data):
        tagline = THEME_TAGLINES.get(data.get("theme", "earth"), "")
        f = _font(FONT_BOLD, 30)
        y = 175
        for line in tagline.split("\n"):
            draw.text((50, y), line, font=f, fill=C["subtext"])
            y += 42

    def _stat_card(self, draw, data):
        # Card background
        draw.rounded_rectangle([(50, 278), (W-50, 490)], radius=20, fill=C["card"])

        stat = data.get("stat", "—")
        f_stat = _font(FONT_BOLD, _stat_size(stat))
        bbox = draw.textbbox((0, 0), stat, font=f_stat)
        sw, sh = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text(((W - sw)//2, 295), stat, font=f_stat, fill=C["stat"])

        desc = data.get("stat_description", "")
        f_desc = _font(FONT_REGULAR, 28)
        y = 295 + sh + 8
        self._centered(draw, desc, y, f_desc, C["white"], max_w=880)

    def _bullets(self, draw, data):
        bullets = data.get("bullets", [])
        f = _font(FONT_REGULAR, 28)
        y = 515
        for bullet in bullets[:3]:
            # Bullet pill
            draw.rounded_rectangle([(50, y-2), (68, y+28)], radius=4, fill=C["stat"])
            y = self._left_text(draw, bullet, x=90, y=y, font=f, color=C["white"], max_w=950)
            y += 18

    def _cta(self, draw, data):
        cta = data.get("cta", "")
        f = _font(FONT_BOLD, 36)
        draw.rectangle([(0, 730), (W, 734)], fill=C["accent_line"])
        self._centered(draw, cta, 755, f, C["cta"], max_w=900)

    def _footer(self, draw, data):
        draw.rectangle([(0, 855), (W, 860)], fill=C["card"])
        draw.rectangle([(0, 860), (W, H)], fill=C["deco"])
        f = _font(FONT_REGULAR, 22)
        draw.text((50, 875), "juteverde.com", font=f, fill=C["stat"])
        hashtags = data.get("hashtags", "#JuteVerde #SustainablePackaging #EcoFriendly #GoGreen")
        draw.text((50, 910), hashtags, font=f, fill=C["subtext"])

    # ------------------------------------------------------------------ #

    def _centered(self, draw, text, y, font, color, max_w=900) -> int:
        for line in self._wrap(draw, text, font, max_w):
            bbox = draw.textbbox((0, 0), line, font=font)
            lw, lh = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text(((W-lw)//2, y), line, font=font, fill=color)
            y += lh + 8
        return y

    def _left_text(self, draw, text, x, y, font, color, max_w) -> int:
        for line in self._wrap(draw, text, font, max_w - x):
            bbox = draw.textbbox((0, 0), line, font=font)
            lh = bbox[3]-bbox[1]
            draw.text((x, y), line, font=font, fill=color)
            y += lh + 6
        return y

    @staticmethod
    def _wrap(draw, text, font, max_w) -> list:
        words = text.split()
        lines, current = [], []
        for word in words:
            test = " ".join(current + [word])
            if draw.textbbox((0, 0), test, font=font)[2] > max_w and current:
                lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            lines.append(" ".join(current))
        return lines


def next_theme(recent_posts: list) -> str:
    used = [p.get("theme", "") for p in recent_posts]
    for theme in THEME_ORDER:
        if theme not in used[-4:]:
            return theme
    return THEME_ORDER[len(recent_posts) % len(THEME_ORDER)]
