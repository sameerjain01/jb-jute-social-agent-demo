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
    "spring": {
        "label":      "SPRING",
        "tagline":    "Chain stores sell packaged memories.\nWe bake the real thing every morning.",
        "bad_emoji":  "🏭",
        "good_emoji": "🌸",
        "bg_prompt":  "cute anime little girl big googly eyes wide smile holding a strawberry shortcake, bakery background spring flowers pink soft bokeh, warm pastel colors",
    },
    "summer": {
        "label":      "SUMMER",
        "tagline":    "Frozen muffins from a factory floor.\nThe kind grandma made — ours come close.",
        "bad_emoji":  "📦",
        "good_emoji": "👵",
        "bg_prompt":  "happy smiling baby with big eyes holding a blueberry muffin, soft warm bakery background bokeh, joyful adorable, pastel tones",
    },
    "fall": {
        "label":      "AUTUMN",
        "tagline":    "Supermarkets sell pumpkin flavouring.\nWe sell the smell that fills your kitchen.",
        "bad_emoji":  "🛒",
        "good_emoji": "🏡",
        "bg_prompt":  "cute anime little girl big round eyes happy holding pumpkin spice roll, cozy autumn bakery window warm orange bokeh, kawaii style",
    },
    "winter": {
        "label":      "WINTER",
        "tagline":    "Chain cookies taste like nothing at all.\nEach bite here takes you somewhere warm.",
        "bad_emoji":  "🏪",
        "good_emoji": "❤️",
        "bg_prompt":  "happy smiling family mother and child big smiles decorating gingerbread cookies together warm kitchen bokeh, joyful festive holiday, soft warm light",
    },
}

THEME_ORDER  = ["spring", "summer", "fall", "winter"]
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
