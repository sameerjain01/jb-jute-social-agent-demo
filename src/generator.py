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

EMOTIONAL_HOOKS = {
    "nostalgia":   "This topic should trigger NOSTALGIA. Tap into the smell of a grandmother's kitchen, "
                   "childhood Saturday mornings, or a recipe passed down untouched. The reader should "
                   "feel pulled back to a specific warm memory they did not know they were carrying.",
    "comfort":     "This topic should deliver COMFORT. Think rainy day, long week, sanctuary. "
                   "Warmth, softness, and the feeling of being held. The bakery is a safe place.",
    "celebration": "This topic should radiate CELEBRATION. Joy, pride, feeling seen and special. "
                   "A birthday cake is love made physical. Make the reader feel that.",
    "pride":       "This topic should evoke PRIDE and ACHIEVEMENT. Relief after hard work, the feeling "
                   "of a chapter closing and a new one opening. Something earned.",
    "grief":       "This topic requires GENTLENESS and CARE. Food heals when words fail. "
                   "Write with quiet warmth — no performance, no brightness. Just presence.",
    "love":        "This topic is about LOVE and COMMITMENT. Romance, shared history, "
                   "the private intimacy of two people becoming one. Specific and tender.",
    "apology":     "This topic is about VULNERABILITY and HEALING. A pastry as a peace offering — "
                   "it says 'I know you, I am sorry, and I tried.' Honest and soft.",
    "wonder":      "This topic should spark CHILDLIKE WONDER. Looking through the glass case, "
                   "watching the baker work, the pastry case as a toy shop window. Awaken curiosity.",
    "community":   "This topic is about BELONGING. The third place, knowing the baker's name, "
                   "a neighbourhood hub. People need places where they are known.",
    "military":    "This topic carries DEEP GRATITUDE and LONGING FOR HOME. A care package crossing "
                   "6,000 miles. The smell of a cookie as an emotional lifeline. Write with reverence.",
    "americana":   "This topic is about COLLECTIVE PRIDE and SUMMER JOY. Flag cakes, "
                   "apple pie, fireworks on the lawn. Freedom celebrated at the table, together.",
}

FORMAT_INSTRUCTIONS = {
    "educate": """
You are writing an EDUCATIONAL post. Keep it tight — 3 punchy paragraphs max.
  1. Line 1: one fact or image so specific it stops the scroll. No warmup.
  2. Middle: one sharp insight. One paragraph. Done.
  3. Last line: a question or observation — 1 sentence, invites a reply.
""",
    "pitch": """
You are writing a PITCH post. Short and sharp — no wasted words.
  1. Line 1: name exactly what the reader is feeling or missing. Hit it directly.
  2. One sentence on why chain alternatives fail — specific, not vague.
  3. One sentence on what Sarah's does instead — show, don't explain.
  4. Final line: soft invite. "We open at 7." "DM to order." Nothing more.
""",
    "cta": """
You are writing a CALL-TO-ACTION post. Urgency, one action, done.
  1. Line 1: the reason to act NOW. Limited batch, deadline, seasonal end.
  2. ONE action — visit, DM, tag someone. State it plainly.
  3. Final line: make the action impossible to miss.
""",
}


class ContentGenerator:
    MODEL = "llama-3.3-70b-versatile"

    def __init__(self, api_key: str, config: dict):
        self.client = Groq(api_key=api_key)
        self.company = config["company"]
        self.content_cfg = config["content"]

    def generate(self, topic: str, format_type: str, emotion: str = "") -> str:
        prompt = self._build_prompt(topic, format_type, emotion)
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

    def _build_prompt(self, topic: str, format_type: str, emotion: str = "") -> str:
        fmt_instruction = FORMAT_INSTRUCTIONS.get(format_type, FORMAT_INSTRUCTIONS["educate"])
        emotional_instruction = EMOTIONAL_HOOKS.get(emotion, "")

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

EMOTIONAL DIRECTION:
{emotional_instruction if emotional_instruction else "Write with warmth and specificity. Tap into memory, comfort, or wonder as the topic suggests."}

SARAH'S BRAND VOICE — warm, specific, and real. Like a baker talking to a regular, not a brand manager:
  - Line 1 must be impossible to scroll past. A number, a smell, a feeling, a bold claim.
  - Every sentence must earn its place. If it does not add something, cut it.
  - Memory and emotion are the product. The muffin is just the vehicle.
    A warm kitchen. A grandmother. The smell that pulls you back 20 years. That is what sells.
  - One idea per post. Say it clearly. Stop.
  - Talk to ONE person: "you", never "our customers" or "everyone"
  - Sound like the person who woke up at 4am to make this — not someone writing about them
  - BANNED phrases: "made with love", "artisan quality", "farm to table", "guilt-free",
    "treat yourself to", "perfect for any occasion", "baked to perfection", "a little something special",
    "we take pride in", "quality ingredients", "passion for baking", "something for everyone"

OUTPUT:
  Return ONLY the post text. No preamble, no "Here is your post:", no markdown.
"""
