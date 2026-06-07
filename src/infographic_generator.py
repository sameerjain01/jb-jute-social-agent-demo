"""
infographic_generator.py
------------------------
Bold 1080x1080 split-panel infographic.
Left = plastic/synthetic (bad). Right = jute (good).
Emoji illustrations downloaded from Twemoji (open source).
"""

import io
import logging
import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

W, H = 1080, 1080

C = {
    "bg":          (27,  67,  50),
    "deco":        (22,  55,  41),
    "card_bad":    (65,  28,  28),
    "card_good":   (36,  87,  65),
    "stat":        (149, 213, 178),
    "white":       (255, 255, 255),
    "subtext":     (216, 243, 220),
    "cta":         (255, 225, 104),
    "bad_text":    (255, 185, 185),
    "good_text":   (216, 243, 220),
    "red_title":   (220, 100, 100),
    "green_title": (149, 213, 178),
    "accent":      (82,  183, 136),
}

THEME_CONFIG = {
    "ocean": {
        "label":      "OCEAN",
        "tagline":    "Plastic is drowning our oceans.\nJute is the life raft.",
        "bad_emoji":  "1f40b",
        "bad_title":  "PLASTIC WORLD",
        "good_emoji": "1f422",
        "good_title": "JUTE WORLD",
    },
    "earth": {
        "label":      "EARTH",
        "tagline":    "Plastic poisons our soil.\nJute gives it life back.",
        "bad_emoji":  "1f637",
        "bad_title":  "PLASTIC WORLD",
        "good_emoji": "1f331",
        "good_title": "JUTE WORLD",
    },
    "trees": {
        "label":      "FORESTS",
        "tagline":    "Synthetic fibres destroy forests.\nJute regrows every season.",
        "bad_emoji":  "1f3ed",
        "bad_title":  "SYNTHETIC WORLD",
        "good_emoji": "1f333",
        "good_title": "JUTE WORLD",
    },
    "water": {
        "label":      "WATER",
        "tagline":    "Cotton farming empties rivers.\nJute uses a fraction of the water.",
        "bad_emoji":  "1f480",
        "bad_title":  "COTTON WORLD",
        "good_emoji": "1f4a7",
        "good_title": "JUTE WORLD",
    },
}

THEME_ORDER  = ["ocean", "earth", "trees", "water"]
FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
EMOJI_SIZE   = 150
EMOJI_BASE   = "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/{}.png"


def _font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _stat_size(stat):
    n = len(stat)
    if n <= 4:  return 115
    if n <= 6:  return 92
    return 74


def _get_emoji(codepoint: str) -> Image.Image | None:
    try:
        url = EMOJI_BASE.format(codepoint)
        with urllib.request.urlopen(url, timeout=6) as r:
            data = r.read()
        img = Image.open(io.BytesIO(data)).convert("RGBA")
        return img.resize((EMOJI_SIZE, EMOJI_SIZE), Image.LANCZOS)
    except Exception as e:
        logger.warning(f"Emoji download failed ({codepoint}): {e}")
        return None


class InfographicGenerator:

    def __init__(self, output_dir="/tmp"):
        self.output_dir = output_dir

    def generate(self, data: dict, run_id: str) -> str:
        canvas = Image.new("RGB", (W, H), C["bg"])
        draw   = ImageDraw.Draw(canvas)
        theme  = data.get("theme", "earth")
        tcfg   = THEME_CONFIG.get(theme, THEME_CONFIG["earth"])

        self._deco_bg(draw)
        self._header(draw, tcfg)
        self._stat_block(draw, data)
        self._split_panels(canvas, draw, data, tcfg)
        self._cta(draw, data)
        self._footer(draw, data)

        path = os.path.join(self.output_dir, f"{run_id}_infographic.png")
        canvas.save(path, "PNG")
        logger.info(f"Infographic saved: {path}")
        return path

    def _deco_bg(self, draw):
        draw.ellipse([(720, -160), (1180, 300)], fill=C["deco"])
        draw.ellipse([(-120, 820), (180, 1120)], fill=C["deco"])

    def _header(self, draw, tcfg):
        draw.text((50, 42), "JuteVerde", font=_font(FONT_BOLD, 56), fill=C["white"])
        f = _font(FONT_REGULAR, 26)
        label = tcfg["label"]
        bbox = draw.textbbox((0, 0), label, font=f)
        draw.text((W - (bbox[2]-bbox[0]) - 50, 58), label, font=f, fill=C["stat"])
        draw.rectangle([(0, 140), (W, 144)], fill=C["accent"])

    def _stat_block(self, draw, data):
        tagline = data.get("tagline", "")
        if tagline:
            f_tag = _font(FONT_BOLD, 28)
            y = 155
            for line in tagline.split("\n"):
                draw.text((50, y), line, font=f_tag, fill=C["subtext"])
                y += 40

        stat = data.get("stat", "—")
        f_stat = _font(FONT_BOLD, _stat_size(stat))
        bbox = draw.textbbox((0, 0), stat, font=f_stat)
        sw, sh = bbox[2]-bbox[0], bbox[3]-bbox[1]
        sy = 238
        draw.text(((W-sw)//2, sy), stat, font=f_stat, fill=C["stat"])

        desc = data.get("stat_description", "")
        self._centered(draw, desc, sy+sh+5, _font(FONT_REGULAR, 24), C["subtext"], max_w=750)

    def _split_panels(self, canvas, draw, data, tcfg):
        PAD, MID  = 20, W // 2
        TOP, BOT  = 340, 748

        draw.rounded_rectangle([(PAD, TOP), (MID-PAD, BOT)], radius=16, fill=C["card_bad"])
        draw.rounded_rectangle([(MID+PAD, TOP), (W-PAD, BOT)], radius=16, fill=C["card_good"])

        f_title = _font(FONT_BOLD, 24)
        self._panel_center_text(draw, tcfg["bad_title"],  PAD, MID-PAD, TOP+16, f_title, C["red_title"])
        self._panel_center_text(draw, tcfg["good_title"], MID+PAD, W-PAD, TOP+16, f_title, C["green_title"])

        bad_img  = _get_emoji(tcfg["bad_emoji"])
        good_img = _get_emoji(tcfg["good_emoji"])
        ey = TOP + 55

        if bad_img:
            ex = (PAD + MID - PAD) // 2 - EMOJI_SIZE // 2
            canvas.paste(bad_img, (ex, ey), bad_img)
        else:
            self._panel_center_text(draw, "✕", PAD, MID-PAD, ey+40, _font(FONT_BOLD, 80), C["red_title"])

        if good_img:
            ex = (MID + PAD + W - PAD) // 2 - EMOJI_SIZE // 2
            canvas.paste(good_img, (ex, ey), good_img)
        else:
            self._panel_center_text(draw, "✓", MID+PAD, W-PAD, ey+40, _font(FONT_BOLD, 80), C["green_title"])

        f_b  = _font(FONT_REGULAR, 23)
        by   = ey + EMOJI_SIZE + 18

        for pt in data.get("bad_points", [])[:3]:
            draw.text((PAD+16, by), "✕", font=f_b, fill=C["red_title"])
            by = self._left_text(draw, pt, PAD+40, by, f_b, C["bad_text"], MID-PAD-12)
            by += 12

        by = ey + EMOJI_SIZE + 18
        for pt in data.get("good_points", [])[:3]:
            draw.text((MID+PAD+16, by), "✓", font=f_b, fill=C["green_title"])
            by = self._left_text(draw, pt, MID+PAD+40, by, f_b, C["good_text"], W-PAD-12)
            by += 12

    def _cta(self, draw, data):
        draw.rectangle([(0, 756), (W, 760)], fill=C["accent"])
        self._centered(draw, data.get("cta", ""), 770, _font(FONT_BOLD, 36), C["cta"], max_w=900)

    def _footer(self, draw, data):
        draw.rectangle([(0, 860), (W, H)], fill=C["deco"])
        f = _font(FONT_REGULAR, 22)
        draw.text((50, 876), "juteverde.com", font=f, fill=C["stat"])
        draw.text((50, 910), data.get("hashtags", "#JuteVerde #Sustainability"), font=f, fill=C["subtext"])

    def _panel_center_text(self, draw, text, x1, x2, y, font, color):
        bbox = draw.textbbox((0, 0), text, font=font)
        cx = (x1+x2)//2 - (bbox[2]-bbox[0])//2
        draw.text((cx, y), text, font=font, fill=color)

    def _centered(self, draw, text, y, font, color, max_w=900) -> int:
        for line in self._wrap(draw, text, font, max_w):
            bbox = draw.textbbox((0, 0), line, font=font)
            lw, lh = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text(((W-lw)//2, y), line, font=font, fill=color)
            y += lh + 8
        return y

    def _left_text(self, draw, text, x, y, font, color, max_x) -> int:
        for line in self._wrap(draw, text, font, max_x-x):
            bbox = draw.textbbox((0, 0), line, font=font)
            draw.text((x, y), line, font=font, fill=color)
            y += bbox[3]-bbox[1] + 5
        return y

    @staticmethod
    def _wrap(draw, text, font, max_w):
        words = text.split()
        lines, current = [], []
        for word in words:
            test = " ".join(current+[word])
            if draw.textbbox((0,0), test, font=font)[2] > max_w and current:
                lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            lines.append(" ".join(current))
        return lines


def next_theme(post_count: int) -> str:
    return THEME_ORDER[post_count % len(THEME_ORDER)]
