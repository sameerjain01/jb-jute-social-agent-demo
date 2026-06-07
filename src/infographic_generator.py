"""
infographic_generator.py
------------------------
Creates a branded 1080x1080 PNG infographic for each post.
Themes rotate: ocean → earth → trees → water
Saves file to /tmp and returns the path.
"""

import logging
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

W, H = 1080, 1080

# Brand palette (RGB)
C = {
    "green_dark":  (27,  67,  50),
    "green_mid":   (45,  106, 79),
    "green_light": (82,  183, 136),
    "brown_dark":  (107, 66,  38),
    "brown_mid":   (139, 94,  60),
    "cream":       (250, 247, 242),
    "white":       (255, 255, 255),
    "dark":        (26,  26,  26),
    "accent":      (149, 213, 178),
}

THEMES = {
    "ocean":  "OCEAN",
    "earth":  "EARTH",
    "trees":  "FORESTS",
    "water":  "WATER",
}

THEME_TAGLINES = {
    "ocean":  "Our oceans are speaking. Are we listening?",
    "earth":  "The earth needs us now, not tomorrow.",
    "trees":  "Every tree saved is a future protected.",
    "water":  "Clean water begins with cleaner choices.",
}

THEME_ORDER = ["ocean", "earth", "trees", "water"]

FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_ITALIC  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _stat_font_size(stat: str) -> int:
    n = len(stat)
    if n <= 4:  return 130
    if n <= 6:  return 105
    return 85


class InfographicGenerator:

    def __init__(self, output_dir: str = "/tmp"):
        self.output_dir = output_dir

    def generate(self, data: dict, run_id: str) -> str:
        """Build infographic PNG. Returns file path."""
        img  = Image.new("RGB", (W, H), C["cream"])
        draw = ImageDraw.Draw(img)

        self._header(draw, data)
        self._content(draw, data)
        self._footer(draw, data)

        path = os.path.join(self.output_dir, f"{run_id}_infographic.png")
        img.save(path, "PNG")
        logger.info(f"Infographic saved: {path}")
        return path

    # ------------------------------------------------------------------ #
    #  Sections                                                            #
    # ------------------------------------------------------------------ #

    def _header(self, draw, data):
        draw.rectangle([(0, 0), (W, 150)], fill=C["green_dark"])

        # Brand name
        draw.text((50, 42), "JuteVerde", font=_font(FONT_BOLD, 54), fill=C["white"])

        # Theme label (right)
        label = THEMES.get(data.get("theme", "earth"), "EARTH")
        f = _font(FONT_REGULAR, 26)
        text = f"◉  {label}"
        bbox = draw.textbbox((0, 0), text, font=f)
        tw = bbox[2] - bbox[0]
        draw.text((W - tw - 50, 60), text, font=f, fill=C["accent"])

    def _content(self, draw, data):
        y = 175

        # Theme tagline
        tagline = THEME_TAGLINES.get(data.get("theme", "earth"), "")
        draw.text((50, y), tagline, font=_font(FONT_ITALIC, 27), fill=C["brown_mid"])
        y += 40

        # Accent line
        draw.rectangle([(50, y), (720, y + 4)], fill=C["green_light"])
        y += 30

        # Big stat
        stat = data.get("stat", "—")
        f_stat = _font(FONT_BOLD, _stat_font_size(stat))
        bbox = draw.textbbox((0, 0), stat, font=f_stat)
        sw = bbox[2] - bbox[0]
        sh = bbox[3] - bbox[1]
        draw.text(((W - sw) // 2, y), stat, font=f_stat, fill=C["green_dark"])
        y += sh + 10

        # Stat description
        stat_desc = data.get("stat_description", "")
        f_desc = _font(FONT_REGULAR, 28)
        y = self._centered_text(draw, stat_desc, y, f_desc, C["dark"], max_w=800)
        y += 28

        # Bullets
        f_b = _font(FONT_REGULAR, 26)
        for bullet in data.get("bullets", [])[:3]:
            draw.text((50, y), "▶", font=f_b, fill=C["green_mid"])
            y = self._left_text(draw, bullet, x=90, y=y, font=f_b, color=C["dark"], max_w=940)
            y += 10

        y += 15

        # Divider
        draw.rectangle([(50, y), (W - 50, y + 3)], fill=C["accent"])
        y += 22

        # CTA
        cta = data.get("cta", "")
        f_cta = _font(FONT_BOLD, 32)
        y = self._centered_text(draw, cta, y + 8, f_cta, C["brown_dark"], max_w=900)

        # Website (pinned near footer)
        f_web = _font(FONT_REGULAR, 21)
        draw.text((50, 905), "juteverde.com", font=f_web, fill=C["green_mid"])
        draw.text((50, 930), "Sustainable Jute Solutions for Modern Business", font=f_web, fill=C["brown_mid"])

    def _footer(self, draw, data):
        draw.rectangle([(0, 960), (W, H)], fill=C["brown_dark"])
        hashtags = data.get("hashtags", "#SustainablePackaging #JuteVerde #EcoFriendly #GoGreen")
        draw.text((50, 985), hashtags, font=_font(FONT_REGULAR, 22), fill=C["white"])

    # ------------------------------------------------------------------ #
    #  Text helpers                                                        #
    # ------------------------------------------------------------------ #

    def _centered_text(self, draw, text, y, font, color, max_w=900) -> int:
        for line in self._wrap(draw, text, font, max_w):
            bbox = draw.textbbox((0, 0), line, font=font)
            lw = bbox[2] - bbox[0]
            lh = bbox[3] - bbox[1]
            draw.text(((W - lw) // 2, y), line, font=font, fill=color)
            y += lh + 8
        return y

    def _left_text(self, draw, text, x, y, font, color, max_w=940) -> int:
        for line in self._wrap(draw, text, font, max_w - x):
            bbox = draw.textbbox((0, 0), line, font=font)
            lh = bbox[3] - bbox[1]
            draw.text((x, y), line, font=font, fill=color)
            y += lh + 6
        return y

    @staticmethod
    def _wrap(draw, text: str, font, max_w: int) -> list:
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
