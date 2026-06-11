"""
topic_selector.py
-----------------
Picks the next topic + format based on:
  - Recent post history (avoids repeating topics within the window)
  - Format rotation (cycles educate → pitch → cta)
"""

import random
import logging

logger = logging.getLogger(__name__)


class TopicSelector:
    FORMAT_CYCLE = ["educate", "pitch", "cta"]

    def __init__(self, topics: list, config: dict):
        self.topics = topics  # list of topic dicts from topics.yaml
        self.window = config["posting"]["min_similarity_window"]

    def select(self, recent_posts: list) -> tuple[str, str, str]:
        """
        Returns (topic_name, format_type).

        recent_posts: list of dicts with keys 'topic' and 'format',
                      ordered newest-first. Comes from SheetsWriter.
        """
        # --- Topic selection ---
        recently_used_topics = {
            p["topic"] for p in recent_posts[: self.window]
        }

        available = [
            t for t in self.topics if t["name"] not in recently_used_topics
        ]

        if not available:
            # Fallback: all topics used recently, reset and pick any
            logger.warning(
                "All topics used in recent window — resetting rotation."
            )
            available = self.topics

        chosen_topic = random.choice(available)
        logger.info(
            f"Available topics: {len(available)}/{len(self.topics)} | "
            f"Chosen: {chosen_topic['id']} - {chosen_topic['name'][:50]}"
        )

        # --- Format selection ---
        # Find what format was last used and advance the cycle
        last_format = recent_posts[0]["format"] if recent_posts else None
        next_format = self._next_format(last_format)

        return chosen_topic["name"], next_format, chosen_topic.get("emotion", "")

    def _next_format(self, last_format: str | None) -> str:
        if last_format is None or last_format not in self.FORMAT_CYCLE:
            return self.FORMAT_CYCLE[0]  # start of cycle

        current_index = self.FORMAT_CYCLE.index(last_format)
        next_index = (current_index + 1) % len(self.FORMAT_CYCLE)
        return self.FORMAT_CYCLE[next_index]
