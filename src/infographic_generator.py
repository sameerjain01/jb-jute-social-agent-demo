"""
infographic_generator.py
------------------------
Renders a 1080x1080 PNG using Playwright (HTML → screenshot).
Hero background fetched from Pollinations.ai (free, no key needed).
Falls back to CSS gradient if image fetch fails.
"""

import base64
import logging
import os
import urllib.parse
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

THEME_CONFIG = {
    "july4": {
        "label":      "JULY 4TH",
        "tagline":    "Any chain can sell a cookie.\nWe make the flag cake your block party remembers.",
        "bad_emoji":  "🏪",
        "good_emoji": "🎆",
        "bg_prompt":  "happy american family big smiles backyard july 4th barbecue flag cake red white blue bokeh summer celebration patriotic joy",
    },
    "veterans": {
        "label":      "VETERANS DAY",
        "tagline":    "Some care packages come from warehouses.\nOurs are baked with a soldier in mind.",
        "bad_emoji":  "📦",
        "good_emoji": "🎖️",
        "bg_prompt":  "proud military veteran in uniform big warm smile family hugging homecoming emotional bokeh american flag soft light grateful",
    },
    "christmas": {
        "label":      "CHRISTMAS",
        "tagline":    "Store-bought cookies sit on shelves for months.\nOurs are gone before the carols end.",
        "bad_emoji":  "🏭",
        "good_emoji": "🎄",
        "bg_prompt":  "happy children big googly eyes wide smiles decorating christmas cookies together warm cozy kitchen bokeh festive holiday lights family joy",
    },
    "summer": {
        "label":      "SUMMER",
        "tagline":    "Gas station snacks are for the road.\nWe are for the destination.",
        "bad_emoji":  "🛒",
        "good_emoji": "☀️",
        "bg_prompt":  "happy smiling children big eyes summer vacation picnic fresh baked treats warm golden sunlight bokeh joyful family beach blanket",
    },
    "birthday": {
        "label":      "BIRTHDAY",
        "tagline":    "A grocery store cake says you forgot.\nOurs says you planned for this moment.",
        "bad_emoji":  "🏪",
        "good_emoji": "🎂",
        "bg_prompt":  "cute child big round eyes wide smile blowing out birthday candles beautiful custom cake colorful bokeh celebration family joy adorable",
    },
    "graduation": {
        "label":      "GRADUATION",
        "tagline":    "Four years of hard work.\nDeserves more than a sheet cake from a box.",
        "bad_emoji":  "📦",
        "good_emoji": "🎓",
        "bg_prompt":  "proud graduate big smile cap and gown family hugging custom graduation cake celebration warm bokeh achievement emotional proud parents",
    },
    "firstcar": {
        "label":      "FIRST CAR",
        "tagline":    "First keys. First freedom.\nCelebrate with something worth remembering.",
        "bad_emoji":  "🏭",
        "good_emoji": "🚗",
        "bg_prompt":  "excited teenager big eyes wide smile holding car keys happy parents celebrating bakery gift box surprise bokeh warm joyful milestone",
    },
    "newhome": {
        "label":      "NEW HOME",
        "tagline":    "Moving boxes empty fast.\nA warm pastry box makes a house feel like home.",
        "bad_emoji":  "🛒",
        "good_emoji": "🏡",
        "bg_prompt":  "happy family smiling new home front door housewarming gift bakery box warm soft bokeh joyful new beginning husband wife children",
    },
    "wedding": {
        "label":      "WEDDING",
        "tagline":    "A wedding cake is not a product.\nIt is the first thing you share as one.",
        "bad_emoji":  "📦",
        "good_emoji": "💍",
        "bg_prompt":  "beautiful bride and groom big smiles cutting wedding cake elegant romantic bokeh floral white gold warm light love celebration",
    },
    "newbaby": {
        "label":      "NEW BABY",
        "tagline":    "A new life calls for something sweet.\nNot a frozen pastry from a shelf.",
        "bad_emoji":  "🏪",
        "good_emoji": "👶",
        "bg_prompt":  "adorable newborn baby big eyes tiny smile happy parents holding infant warm soft pastel light bakery gift box bokeh pink blue joy",
    },
    "anniversary": {
        "label":      "ANNIVERSARY",
        "tagline":    "Every year together deserves a ritual.\nMake this one sweet.",
        "bad_emoji":  "🏭",
        "good_emoji": "❤️",
        "bg_prompt":  "happy couple big smiles anniversary sharing cake warm romantic bokeh golden light love celebration elegant restaurant candles",
    },
    "milestone": {
        "label":      "MILESTONE",
        "tagline":    "Not every win has a name.\nAll of them deserve to be celebrated.",
        "bad_emoji":  "🛒",
        "good_emoji": "⭐",
        "bg_prompt":  "happy family big smiles celebrating life achievement custom cake confetti warm bokeh joyful success proud moment children laughing",
    },
}

THEME_ORDER = [
    "birthday", "july4", "christmas", "graduation",
    "wedding", "newbaby", "summer", "anniversary",
    "veterans", "newhome", "firstcar", "milestone",
]
TEMPLATE_PATH = Path(__file__).parent / "infographic_template.html"
POLLINATIONS  = "https://image.pollinations.ai/prompt/{}?width=1080&height=420&nologo=true&seed=42"


def next_theme(post_count: int) -> str:
    return THEME_ORDER[post_count % len(THEME_ORDER)]


def _stat_class(stat: str) -> str:
    return "long" if len(stat) > 6 else ""


def _escape(text: str) -> str:
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def _fetch_bg(prompt: str) -> str:
    """Returns a base64 data URL, or empty string on failure."""
    try:
        url = POLLINATIONS.format(urllib.parse.quote(prompt))
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        b64 = base64.b64encode(data).decode()
        mime = "image/jpeg"
        return f"data:{mime};base64,{b64}"
    except Exception as e:
        logger.warning(f"Background fetch failed: {e}")
        return ""


class InfographicGenerator:

    def __init__(self, output_dir="/tmp"):
        self.output_dir = output_dir

    def generate(self, data: dict, run_id: str) -> str:
        theme = data.get("theme", "summer")
        tcfg  = THEME_CONFIG.get(theme, THEME_CONFIG["summer"])

        logger.info(f"Fetching background image for theme: {theme}")
        bg_data_url = _fetch_bg(tcfg["bg_prompt"])
        bg_css = f"url('{bg_data_url}')" if bg_data_url else (
            "linear-gradient(160deg, #c0334d 0%, #8b1a2e 100%)"
        )

        tagline_parts = (data.get("tagline") or tcfg["tagline"]).split("\n", 1)
        tagline_line1 = tagline_parts[0] if len(tagline_parts) > 0 else ""
        tagline_line2 = tagline_parts[1] if len(tagline_parts) > 1 else ""

        bad_points  = data.get("bad_points",  ["", "", ""])
        good_points = data.get("good_points", ["", "", ""])

        html = TEMPLATE_PATH.read_text(encoding="utf-8")

        replacements = {
            "{{BG_CSS}}":        bg_css,
            "{{SEASON}}":        _escape(tcfg["label"]),
            "{{TAGLINE_LINE1}}": _escape(tagline_line1),
            "{{TAGLINE_LINE2}}": _escape(tagline_line2),
            "{{STAT}}":          _escape(data.get("stat", "—")),
            "{{STAT_CLASS}}":    _stat_class(data.get("stat", "")),
            "{{STAT_DESC}}":     _escape(data.get("stat_description", "")),
            "{{BAD_EMOJI}}":     tcfg["bad_emoji"],
            "{{GOOD_EMOJI}}":    tcfg["good_emoji"],
            "{{BAD_1}}":         _escape(bad_points[0] if len(bad_points) > 0 else ""),
            "{{BAD_2}}":         _escape(bad_points[1] if len(bad_points) > 1 else ""),
            "{{BAD_3}}":         _escape(bad_points[2] if len(bad_points) > 2 else ""),
            "{{GOOD_1}}":        _escape(good_points[0] if len(good_points) > 0 else ""),
            "{{GOOD_2}}":        _escape(good_points[1] if len(good_points) > 1 else ""),
            "{{GOOD_3}}":        _escape(good_points[2] if len(good_points) > 2 else ""),
            "{{CTA}}":           _escape(data.get("cta", "")),
            "{{HASHTAGS}}":      _escape(data.get("hashtags", "#SarahsBakery")),
        }

        for placeholder, value in replacements.items():
            html = html.replace(placeholder, value)

        html_path = os.path.join(self.output_dir, f"{run_id}_infographic.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

        output_path = os.path.join(self.output_dir, f"{run_id}_infographic.png")
        self._screenshot(html_path, output_path)
        os.remove(html_path)

        logger.info(f"Infographic saved: {output_path}")
        return output_path

    def _screenshot(self, html_path: str, output_path: str) -> None:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1080, "height": 1080})
            page.goto(f"file://{os.path.abspath(html_path)}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)   # let fonts finish rendering
            page.screenshot(path=output_path, clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
            browser.close()
