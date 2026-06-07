"""
generator.py
------------
Calls Gemini to write a LinkedIn post given a topic and format type.
Format types:  educate | pitch | cta
"""

import logging
import google.generativeai as genai

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
    MODEL = "gemini-2.0-flash"

    def __init__(self, api_key: str, config: dict):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.MODEL)
        self.company = config["company"]
        self.content_cfg = config["content"]

    def generate(self, topic: str, format_type: str) -> str:
        prompt = self._build_prompt(topic, format_type)
        logger.debug(f"Prompt length: {len(prompt)} chars")

        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.85,       # creative but not wild
                max_output_tokens=600,
            ),
        )
        return response.text.strip()

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
  - Use {self.content_cfg['emoji_count']} emojis placed naturally (not all at the start)
  - Use line breaks between paragraphs for readability
  - End with exactly {self.content_cfg['hashtag_count']} relevant hashtags on their own line
  - Do NOT use generic filler phrases like "In today's world" or "It's no secret"
  - Cite specific numbers/percentages where you use them (make them realistic)
  - Never mention competitor brand names
  - Never make political statements

OUTPUT:
  Return ONLY the post text. No preamble, no "Here is your post:", no markdown.
"""
