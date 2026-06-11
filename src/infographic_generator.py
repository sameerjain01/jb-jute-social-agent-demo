"""
infographic_generator.py
------------------------
Bold 1080x1080 split-panel infographic.
Left = chain/mass-produced (bad). Right = Sarah's Bakery (good).
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
    "bg":           (44,  26,  14),   # dark chocolate
    "deco":         (26,  12,   6),   # deeper chocolate
    "card_bad":     (45,  45,  45),   # cold industrial grey (chain store)
    "card_good":    (122, 61,  21),   # warm caramel (Sarah's)
    "stat":         (245, 222, 179),  # warm cream
    "white":        (255, 255, 255),
    "subtext":      (250, 235, 215),  # antique white
    "cta":          (255, 182, 193),  # blush pink
    "bad_text":     (176, 176, 176),  # cold grey
    "good_text":    (250, 235, 215),  # warm cream
    "bad_title":    (140, 140, 140),  # muted grey
    "good_title":   (222, 184, 135),  # burlywood gold
    "accent":       (198, 140,  58),  # warm amber
}

THEME_CONFIG = {
    "spring": {
        "label":      "SPRING",
        "tagline":    "Chain stores thaw frozen pastries.\nWe bake with strawberries picked this week.",
        "bad_emoji":  "1f3ed",   # factory
        "bad_title":  "CHAIN STORE",
        "good_emoji": "1f370",   # shortcake / strawberry tart
        "good_title": "SARAH'S BAKERY",
    },
    "summer": {
        "label":      "SUMMER",
        "tagline":    "Supermarkets ship muffins from factories.\nOurs come out of the oven at 6am.",
        "bad_emoji":  "1f9ca",   # ice cube (frozen)
        "bad_title":  "CHAIN STORE",
        "good_emoji": "1f9c1",   # cupcake
        "good_title": "SARAH'S BAKERY",
    },
    "fall": {
        "label":      "AUTUMN",
        "tagline":    "Boxed pumpkin flavouring sits on shelves for months.\nOur rolls are gone by noon.",
        "bad_emoji":  "1f4e6",   # box / packaged goods
        "bad_title":  "CHAIN STORE",
        "good_emoji": "1f383",   # jack-o-lantern / pumpkin
        "good_title": "SARAH'S BAKERY",
    },
    "winter": {
        "label":      "WINTER",
        "tagline":    "Pre-made chains cut every corner.\nWe make every cookie by hand.",
        "bad_emoji":  "1f6d2",   # shopping cart / supermarket
        "bad_title":  "CHAIN STORE",
        "good_emoji": "1f36a",   # cookie
        "good_title": "SARAH'S BAKERY",
    },
}

THEME_ORDER  = ["spring", "summer", "fall", "winter"]
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
        theme  = data.get("theme", "summer")
        tcfg   = THEME_CONFIG.get(theme, THEME_CONFIG["summer"])

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
        draw.text((50, 42), "Sarah's Bakery", font=_font(FONT_BOLD, 52), fill=C["white"])
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
        self._panel_center_text(draw, tcfg["bad_title"],  PAD, MID-PAD, TOP+16, f_title, C["bad_title"])
        self._panel_center_text(draw, tcfg["good_title"], MID+PAD, W-PAD, TOP+16, f_title, C["good_title"])

        bad_img  = _get_emoji(tcfg["bad_emoji"])
        good_img = _get_emoji(tcfg["good_emoji"])
        ey = TOP + 55

        if bad_img:
            ex = (PAD + MID - PAD) // 2 - EMOJI_SIZE // 2
            canvas.paste(bad_img, (ex, ey), bad_img)
        else:
            self._panel_center_text(draw, "✕", PAD, MID-PAD, ey+40, _font(FONT_BOLD, 80), C["bad_title"])

        if good_img:
            ex = (MID + PAD + W - PAD) // 2 - EMOJI_SIZE // 2
            canvas.paste(good_img, (ex, ey), good_img)
        else:
            self._panel_center_text(draw, "✓", MID+PAD, W-PAD, ey+40, _font(FONT_BOLD, 80), C["good_title"])

        f_b  = _font(FONT_REGULAR, 23)
        by   = ey + EMOJI_SIZE + 18

        for pt in data.get("bad_points", [])[:3]:
            draw.text((PAD+16, by), "✕", font=f_b, fill=C["bad_title"])
            by = self._left_text(draw, pt, PAD+40, by, f_b, C["bad_text"], MID-PAD-12)
            by += 12

        by = ey + EMOJI_SIZE + 18
        for pt in data.get("good_points", [])[:3]:
            draw.text((MID+PAD+16, by), "✓", font=f_b, fill=C["good_title"])
            by = self._left_text(draw, pt, MID+PAD+40, by, f_b, C["good_text"], W-PAD-12)
            by += 12

    def _cta(self, draw, data):
        draw.rectangle([(0, 756), (W, 760)], fill=C["accent"])
        self._centered(draw, data.get("cta", ""), 770, _font(FONT_BOLD, 36), C["cta"], max_w=900)

    def _footer(self, draw, data):
        draw.rectangle([(0, 860), (W, H)], fill=C["deco"])
        f = _font(FONT_REGULAR, 22)
        draw.text((50, 876), "sarahsbakes.com", font=f, fill=C["stat"])
        draw.text((50, 910), data.get("hashtags", "#SarahsBakery #FreshBaked"), font=f, fill=C["subtext"])

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
