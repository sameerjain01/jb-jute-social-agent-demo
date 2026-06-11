"""
infographic_generator.py
------------------------
Renders a 1080x1080 infographic PNG using Playwright (HTML → screenshot).
Google Fonts, CSS gradients, proper typography — no more Pillow.
Seasonal themes tied to family memory and emotional moments.
"""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

THEME_CONFIG = {
    "spring": {
        "label":      "SPRING",
        "tagline":    "Chain stores sell packaged memories.\nWe bake the real thing every morning.",
        "bad_emoji":  "🏭",
        "good_emoji": "🌸",
    },
    "summer": {
        "label":      "SUMMER",
        "tagline":    "Frozen muffins from a factory floor.\nThe kind grandma made — ours come close.",
        "bad_emoji":  "📦",
        "good_emoji": "👵",
    },
    "fall": {
        "label":      "AUTUMN",
        "tagline":    "Supermarkets sell pumpkin flavouring.\nWe sell the smell that fills your kitchen.",
        "bad_emoji":  "🛒",
        "good_emoji": "🏡",
    },
    "winter": {
        "label":      "WINTER",
        "tagline":    "Chain cookies taste like nothing at all.\nEach bite here takes you somewhere warm.",
        "bad_emoji":  "🏪",
        "good_emoji": "❤️",
    },
}

THEME_ORDER = ["spring", "summer", "fall", "winter"]

TEMPLATE_PATH = Path(__file__).parent / "infographic_template.html"


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


class InfographicGenerator:

    def __init__(self, output_dir="/tmp"):
        self.output_dir = output_dir

    def generate(self, data: dict, run_id: str) -> str:
        theme  = data.get("theme", "summer")
        tcfg   = THEME_CONFIG.get(theme, THEME_CONFIG["summer"])

        tagline_parts = (data.get("tagline") or tcfg["tagline"]).split("\n", 1)
        tagline_line1 = tagline_parts[0] if len(tagline_parts) > 0 else ""
        tagline_line2 = tagline_parts[1] if len(tagline_parts) > 1 else ""

        bad_points  = data.get("bad_points",  ["", "", ""])
        good_points = data.get("good_points", ["", "", ""])

        html = TEMPLATE_PATH.read_text(encoding="utf-8")

        replacements = {
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
            page.screenshot(path=output_path, clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
            browser.close()
