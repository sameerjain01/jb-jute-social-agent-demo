"""
guardrail.py
------------
Second Gemini call that acts as an independent compliance judge.
Returns structured JSON: { pass, score, flags, reason }

Completely separate from the generator — different prompt, different role.
"""

import json
import logging
import re
import google.generativeai as genai

logger = logging.getLogger(__name__)

GUARDRAIL_PROMPT = """You are a strict content compliance judge for a sustainable small business brand on LinkedIn.

Your job: evaluate whether a post is safe, appropriate, and on-brand to publish WITHOUT human review.

EVALUATION CRITERIA — reject if ANY of these are true:
  ❌ Contains offensive, racist, sexist, derogatory, or discriminatory language
  ❌ Contains personal attacks or shames any individual or group
  ❌ Makes false, unverifiable, or exaggerated claims (e.g. "100% carbon neutral" with no basis)
  ❌ Is unrelated to sustainability, jute, eco-friendly products, or business
  ❌ Mentions competitor brand names
  ❌ Makes political or religious statements
  ❌ Is pure spam with no educational or informational value
  ❌ Could damage a professional brand's reputation
  ❌ Is duplicate or near-identical to a post that was recently published

SCORING (1–10):
  9–10: Excellent — highly on-brand, specific, engaging
  7–8:  Good — solid post, minor improvements possible
  6:    Acceptable — passes but weak
  1–5:  Poor — reject

RESPOND WITH VALID JSON ONLY. No preamble, no markdown, no explanation outside the JSON.

{
  "pass": true or false,
  "score": <integer 1-10>,
  "flags": ["list of specific issues found, empty if none"],
  "reason": "one sentence summary of your decision"
}

POST TO EVALUATE:
---
{post_content}
---

RECENT POST TOPICS (to detect near-duplicates):
{recent_topics}
"""


class GuardrailJudge:
    MODEL = "gemini-1.5-flash"

    def __init__(self, api_key: str, config: dict):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.MODEL)
        self.min_score = config["guardrail"]["min_pass_score"]

    def evaluate(self, post_content: str, recent_topics: list = None) -> dict:
        """
        Returns dict: { pass: bool, score: int, flags: list, reason: str }
        Never raises — on any error, returns a safe fail result.
        """
        recent_str = ", ".join(recent_topics) if recent_topics else "none"

        prompt = GUARDRAIL_PROMPT.format(
            post_content=post_content,
            recent_topics=recent_str,
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,        # low temp = consistent judgement
                    max_output_tokens=300,
                ),
            )
            raw = response.text.strip()
            result = self._parse_response(raw)

            # Enforce minimum score threshold
            if result["pass"] and result["score"] < self.min_score:
                result["pass"] = False
                result["reason"] = (
                    f"Score {result['score']} is below minimum threshold {self.min_score}. "
                    + result["reason"]
                )

            return result

        except Exception as e:
            logger.error(f"Guardrail evaluation error: {e}")
            return {
                "pass": False,
                "score": 0,
                "flags": ["guardrail_error"],
                "reason": f"Guardrail evaluation failed: {str(e)}",
            }

    def _parse_response(self, raw: str) -> dict:
        """Extract JSON from response, handling minor formatting issues."""
        # Strip any accidental markdown fences
        clean = re.sub(r"```json|```", "", raw).strip()

        try:
            data = json.loads(clean)
            # Validate expected keys exist
            return {
                "pass": bool(data.get("pass", False)),
                "score": int(data.get("score", 0)),
                "flags": data.get("flags", []),
                "reason": str(data.get("reason", "No reason provided")),
            }
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Could not parse guardrail JSON: {e} | Raw: {raw[:200]}")
            return {
                "pass": False,
                "score": 0,
                "flags": ["parse_error"],
                "reason": f"Could not parse guardrail response: {raw[:100]}",
            }
