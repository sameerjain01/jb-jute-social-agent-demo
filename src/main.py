"""
main.py
-------
Orchestrator. Called by GitHub Actions on each run (scheduled or manual).

Flow:
  1. Load config + topics
  2. Read recent post history from Sheets
  3. Select topic + format (rotation logic)
  4. Generate post content (Gemini)
  5. Evaluate with guardrail (Gemini, separate call)
  6. If pass → publish to Feed; if fail → retry up to max_retries
  7. If all retries exhausted → log skip, exit non-zero (GitHub Action = failed run)
"""

import os
import sys
import logging
from pathlib import Path

import yaml

# Add src/ to path so imports work when called from repo root
sys.path.insert(0, str(Path(__file__).parent))

from topic_selector import TopicSelector
from generator import ContentGenerator
from guardrail import GuardrailJudge
from sheets_writer import SheetsWriter
from infographic_generator import InfographicGenerator, next_theme
from drive_uploader import DriveUploader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_config() -> tuple[dict, list]:
    repo_root = Path(__file__).parent.parent
    with open(repo_root / "config" / "config.yaml") as f:
        config = yaml.safe_load(f)
    with open(repo_root / "data" / "topics.yaml") as f:
        topics_data = yaml.safe_load(f)
    return config, topics_data["topics"]


def get_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        logger.error(f"Missing required environment variable: {key}")
        sys.exit(1)
    return value


def run():
    logger.info("=" * 60)
    logger.info("JuteVerde Social Media Agent — starting run")
    logger.info("=" * 60)

    # --- Load config ---
    config, topics = load_config()
    logger.info(f"Loaded {len(topics)} topics from config")

    # --- Load secrets from environment ---
    groq_api_key         = get_env("GROQ_API_KEY")
    google_credentials   = get_env("GOOGLE_CREDENTIALS_JSON")
    spreadsheet_id       = get_env("SPREADSHEET_ID")

    # --- Initialise components ---
    sheets    = SheetsWriter(google_credentials, spreadsheet_id)
    selector  = TopicSelector(topics, config)
    generator = ContentGenerator(groq_api_key, config)
    guardrail = GuardrailJudge(groq_api_key, config)

    # --- Read history ---
    window = config["posting"]["min_similarity_window"]
    recent_posts = sheets.get_recent_posts(n=window)
    logger.info(f"Retrieved {len(recent_posts)} recent posts from Sheets")

    # --- Select topic + format ---
    topic, format_type = selector.select(recent_posts)
    logger.info(f"Selected → topic: '{topic[:60]}' | format: {format_type}")

    # --- Generate + evaluate loop ---
    import datetime
    run_id       = datetime.datetime.utcnow().strftime("RUN_%Y%m%d_%H%M%S")
    max_retries  = config["posting"]["max_retries"]
    recent_topic_names = [p["topic"] for p in recent_posts[:5]]

    for attempt in range(1, max_retries + 1):
        logger.info(f"--- Attempt {attempt}/{max_retries} ---")

        # Generate
        try:
            post_content = generator.generate(topic, format_type)
            logger.info(f"Generated {len(post_content.split())} words")
            logger.debug(f"Content preview: {post_content[:120]}…")
        except Exception as e:
            logger.error(f"Generation failed on attempt {attempt}: {e}")
            continue

        # Guardrail
        result = guardrail.evaluate(post_content, recent_topics=recent_topic_names)
        logger.info(
            f"Guardrail → pass={result['pass']} | score={result['score']} | "
            f"reason: {result['reason']}"
        )
        if result["flags"]:
            logger.warning(f"Flags: {result['flags']}")

        # Log every attempt regardless of outcome
        sheets.log_attempt(run_id, attempt, topic, format_type, post_content, result)

        if result["pass"]:
            sheets.publish_post(run_id, topic, format_type, post_content, result["score"])
            logger.info(f"✅ Post published (score: {result['score']})")

            # --- Infographic ---
            try:
                theme = next_theme(recent_posts)
                logger.info(f"Generating infographic | theme: {theme}")
                infographic_data = generator.generate_infographic_data(topic, theme)
                ig = InfographicGenerator()
                img_path = ig.generate(infographic_data, run_id)
                uploader = DriveUploader(google_credentials)
                drive_url = uploader.upload(img_path, f"{run_id}_infographic.png")
                sheets.publish_infographic(
                    run_id, topic, theme,
                    infographic_data.get("stat", ""),
                    drive_url,
                )
                logger.info(f"✅ Infographic published: {drive_url}")
            except Exception as e:
                logger.error(f"Infographic failed (post still published): {e}")

            logger.info("=" * 60)
            return  # clean exit

        logger.warning(f"Attempt {attempt} rejected. Retrying with new generation…")

    # All attempts failed
    logger.error(f"❌ All {max_retries} attempts failed guardrail — skipping this cycle.")
    sheets.log_skip(run_id, topic, format_type, f"Failed guardrail after {max_retries} attempts")
    sys.exit(1)  # marks GitHub Actions run as failed — visible in UI


if __name__ == "__main__":
    run()
