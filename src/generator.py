"""
generator.py
------------
Calls Groq to write an Instagram post and infographic content for Sarah's Bakery.
Format types:  educate | pitch | cta
"""

import json
import logging
import re

from groq import Groq

logger = logging.getLogger(__name__)

FORMAT_INSTRUCTIONS = {
    "educate": """
You are writing an EDUCATIONAL post.
Structure:
  1. Open with one surprising or specific fact that stops the scroll (1 sentence)
  2. Explain the insight in 2-3 short punchy paragraphs — paint a picture
  3. Connect it to what makes a fresh artisan bakery different
  4. End with a question or observation that invites a reply
""",
    "pitch": """
You are writing a PITCH post.
Structure:
  1. Open by naming something the reader already feels (a morning routine, a craving, a disappointment) — 1 sentence
  2. Show why chain or supermarket alternatives fall short — be specific, not vague
  3. Introduce Sarah's Bakery as the real alternative — show don't tell
  4. End with a soft invite: "come find us", "DM to pre-order", "we open at 7"
""",
    "cta": """
You are writing a CALL-TO-ACTION post.
Structure:
  1. Open with a reason to act now — limited batch, seasonal item ending, pre-order deadline
  2. State ONE clear action (visit us, DM to order, tag a friend who needs this)
  3. Give them a quick reason why it's worth it
  4. Make the action prominent in the final line
""",
}


class ContentGenerator:
    MODEL = "llama-3.3-70b-versatile"

    def __init__(self, api_key: str, config: dict):
        self.client = Groq(api_key=api_key)
        self.company = config["company"]
        self.content_cfg = config["content"]

    def generate(self, topic: str, format_type: str) -> str:
        prompt = self._build_prompt(topic, format_type)
        logger.debug(f"Prompt length: {len(prompt)} chars")

        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()

    def generate_infographic_data(self, topic: str, theme: str) -> dict:
        prompt = f"""Create content for a split-panel Instagram infographic for {self.company['name']}.

Topic: {topic}
Seasonal theme: {theme}

The infographic shows two sides: LEFT = chain store / mass-produced (the problem), RIGHT = Sarah's Bakery (the solution).

RULES:
- stat: ONE striking number displayed very large (e.g. "72hrs" "3x" "6am" "0" "48hrs")
- stat_description: what this stat means, max 8 words — make it land
- tagline: 2 short lines — first line names the chain-store problem, second names the artisan answer
- bad_points: 3 specific facts about chain/supermarket baked goods — be specific, include numbers or timeframes
- good_points: 3 specific Sarah's Bakery facts that directly counter each bad point — include numbers or timeframes
- cta: max 5 words, punchy, action-oriented (e.g. "Order before 8am", "Come find us today")
- NO vague claims. Every point must be specific and visual.

Return ONLY valid JSON:
{{
  "stat": "one striking figure",
  "stat_description": "what this stat means, max 8 words",
  "tagline": "line 1 — the chain-store problem\\nline 2 — the artisan answer",
  "bad_points": [
    "specific chain-store fact with number or timeframe",
    "specific chain-store fact with number or timeframe",
    "specific chain-store fact with number or timeframe"
  ],
  "good_points": [
    "specific Sarah's Bakery fact with number or timeframe",
    "specific Sarah's Bakery fact with number or timeframe",
    "specific Sarah's Bakery fact with number or timeframe"
  ],
  "cta": "punchy action phrase max 5 words",
  "hashtags": "#SarahsBakery #FreshBaked #Tag3 #Tag4 #Tag5 #Tag6 #Tag7 #Tag8"
}}"""

        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=400,
        )
        raw = response.choices[0].message.content.strip()
        clean = re.sub(r"```json|```", "", raw).strip()
        data = json.loads(clean)
        data["theme"] = theme
        return data

    def _build_prompt(self, topic: str, format_type: str) -> str:
        fmt_instruction = FORMAT_INSTRUCTIONS.get(format_type, FORMAT_INSTRUCTIONS["educate"])

        return f"""You are the Instagram content writer for {self.company['name']}.

BAKERY CONTEXT:
  Name: {self.company['name']}
  Tagline: {self.company['tagline']}
  What we do: {self.company['description']}
  Website: {self.company['website']}
  Brand voice: {self.company['voice']}

YOUR TASK:
  Write an Instagram post about this topic: "{topic}"

POST FORMAT:
{fmt_instruction}

WRITING RULES:
  - Length: {self.content_cfg['min_words']}–{self.content_cfg['max_words']} words
  - Use {self.content_cfg['emoji_count']} emojis placed naturally — not at the start of every line
  - Short paragraphs — 2 sentences max each
  - End with exactly {self.content_cfg['hashtag_count']} hashtags on their own line
  - Every claim must be specific and real — no vague generalisations
  - Never mention competitor names

TONE — write like the baker who actually made it, not a social media manager:
  - First line must stop the scroll: a specific detail, a surprising number, or a vivid sensory image
  - Lean into memory and emotion: a warm kitchen, a grandmother's recipe, the smell that fills the house
    on a Sunday morning, a child's face when the box opens. These are the real reasons people come back.
  - Be concrete and sensory — describe what you smell, see, taste, feel
  - Talk directly to the reader: "you", not "our customers"
  - Short sentences. Real words. No filler.
  - BANNED phrases: "made with love", "artisan quality", "farm to table", "guilt-free indulgence",
    "treat yourself to", "perfect for any occasion", "baked to perfection", "a little something special",
    "we take pride in", "quality ingredients", "passion for baking"

OUTPUT:
  Return ONLY the post text. No preamble, no "Here is your post:", no markdown.
"""
