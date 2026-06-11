"""
guardrail.py
------------
Second Groq call that acts as an independent compliance judge.
Returns structured JSON: { pass, score, flags, reason }
"""

import json
import logging
import re
from groq import Groq

logger = logging.getLogger(__name__)

GUARDRAIL_PROMPT = """You are a strict content compliance judge for a neighborhood artisan bakery's Instagram account.

Your job: evaluate whether a post is safe, appropriate, and on-brand to publish WITHOUT human review.

EVALUATION CRITERIA — reject if ANY of these are true:
  ❌ Contains offensive, racist, sexist, derogatory, or discriminatory language
  ❌ Contains personal attacks or shames any individual or group
  ❌ Makes false, unverifiable, or exaggerated claims (e.g. "best in the world" with no basis)
  ❌ Is unrelated to baking, pastries, food, seasonal ingredients, or the bakery business
  ❌ Mentions competitor brand names
  ❌ Makes political or religious statements
  ❌ Makes health or medical claims (e.g. "cures", "boosts immunity")
  ❌ Is pure spam with no educational or informational value
  ❌ Could damage a small business's reputation
  ❌ Is duplicate or near-identical to a post that was recently published

SCORING (1–10):
  9–10: Excellent — highly on-brand, specific, engaging
  7–8:  Good — solid post, minor improvements possible
  6:    Acceptable — passes but weak
  1–5:  Poor — reject

RESPOND WITH VALID JSON ONLY. No preamble, no markdown, no explanation outside the JSON.

{{
  "pass": true or false,
  "score": <integer 1-10>,
  "flags": ["list of specific issues found, empty if none"],
  "reason": "one sentence summary of your decision"
}}

POST TO EVALUATE:
---
{post_content}
---

RECENT POST TOPICS (to detect near-duplicates):
{recent_topics}
"""


class GuardrailJudge:
    MODEL = "llama-3.3-70b-versatile"

    def __init__(self, api_key: str, config: dict):
        self.client = Groq(api_key=api_key)
        self.min_score = config["guardrail"]["min_pass_score"]

    def evaluate(self, post_content: str, recent_topics: list = None) -> dict:
        recent_str = ", ".join(recent_topics) if recent_topics else "none"

        prompt = GUARDRAIL_PROMPT.format(
            post_content=post_content,
            recent_topics=recent_str,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300,
            )
            raw = response.choices[0].message.content.strip()
            result = self._parse_response(raw)

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
        clean = re.sub(r"```json|```", "", raw).strip()

        try:
            data = json.loads(clean)
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
