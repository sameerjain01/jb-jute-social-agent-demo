"""
generator.py
------------
Calls Groq to write a LinkedIn post given a topic and format type.
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
  1. Open with a surprising fact or statistic (the hook — 1 sentence)
  2. Explain the insight in 3-4 short paragraphs
  3. Connect it to a real business implication
  4. End with a thought-provoking question to spark comments
""",
    "pitch": """
You are writing a PITCH post.
Structure:
  1. Open by naming a pain point your audience recognises (1-2 sentences)
  2. Agitate: why this problem is getting worse or costlier
  3. Introduce jute products as the solution — be specific, not vague
  4. End with a single sentence invitation (soft CTA: "DM us" or "see how we can help")
""",
    "cta": """
You are writing a CALL-TO-ACTION post.
Structure:
  1. Open with a compelling reason to act NOW (urgency or opportunity)
  2. State exactly ONE clear action for the reader to take
  3. Briefly explain why this action is worth their time
  4. Make the CTA prominent in the final line (e.g. "👇 Book a free 20-min call")
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
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()

    def generate_infographic_data(self, topic: str, theme: str) -> dict:
        prompt = f"""Create data for a bold social media infographic for {self.company['name']}.

Topic: {topic}
Environmental theme: {theme}

RULES:
- The stat must be a single number/figure that is SHOCKING or surprising (e.g. "8M+" "400yrs" "88%")
- Bullets must each contain a specific number or comparison — NO vague claims
  BAD: "Jute is biodegradable"
  GOOD: "Fully biodegrades in 1-2 years vs 400 years for plastic"
  BAD: "Jute uses less water"
  GOOD: "Uses 88% less water than cotton per kg"
- CTA must be punchy, 5 words max, action-oriented

Return ONLY valid JSON:
{{
  "stat": "shocking single figure (e.g. '8M+' or '88%' or '400yrs')",
  "stat_description": "one line — what this stat means, max 8 words",
  "bullets": [
    "specific stat-backed fact, max 10 words",
    "specific stat-backed fact, max 10 words",
    "specific stat-backed fact, max 10 words"
  ],
  "cta": "punchy action phrase, max 5 words",
  "hashtags": "#Tag1 #Tag2 #Tag3 #Tag4"
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

        return f"""You are the LinkedIn content writer for {self.company['name']}.

COMPANY CONTEXT:
  Name: {self.company['name']}
  Tagline: {self.company['tagline']}
  What we do: {self.company['description']}
  Website: {self.company['website']}
  Brand voice: {self.company['voice']}

YOUR TASK:
  Write a LinkedIn post about this topic: "{topic}"

POST FORMAT:
{fmt_instruction}

WRITING RULES:
  - Length: {self.content_cfg['min_words']}–{self.content_cfg['max_words']} words
  - Use {self.content_cfg['emoji_count']} emojis placed naturally
  - Short paragraphs — 2 sentences max each
  - End with exactly {self.content_cfg['hashtag_count']} hashtags on their own line
  - Every stat or number must be specific and realistic
  - Never mention competitor brand names or make political statements

TONE — write like a knowledgeable founder talking to a peer, not a marketer:
  - First line must STOP THE SCROLL: use a shocking stat, a bold claim, or a direct challenge
  - Be specific and visual — paint a picture, don't summarise
  - Conversational and direct — say "you" not "businesses"
  - No corporate speak. BANNED phrases: "prioritize sustainability", "it's essential to",
    "enhance your brand", "in today's world", "take the first step", "sustainable future",
    "eco-conscious consumers", "it's no secret", "as we all know"

OUTPUT:
  Return ONLY the post text. No preamble, no "Here is your post:", no markdown.
"""
