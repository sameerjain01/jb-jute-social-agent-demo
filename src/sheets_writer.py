"""
sheets_writer.py
----------------
All Google Sheets interactions:
  - Auto-creates tabs and headers on first run
  - Reads recent post history for topic rotation
  - Writes published posts to Feed tab
  - Logs every attempt (pass or fail) to Log tab
  - Logs skipped cycles to Log tab
"""

import json
import logging
from datetime import datetime, timezone

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Tab names
TAB_FEED = "Feed"
TAB_LOG  = "Log"

# Column headers
FEED_HEADERS = [
    "Run ID", "Timestamp (UTC)", "Topic", "Format",
    "Post Content", "Guardrail Score", "Status", "Infographic URL",
]
LOG_HEADERS = [
    "Run ID", "Timestamp (UTC)", "Attempt", "Topic", "Format",
    "Post Content", "Guardrail Score", "Pass", "Flags", "Reason",
]


class SheetsWriter:
    def __init__(self, credentials_json: str, spreadsheet_id: str):
        """
        credentials_json: the full JSON string of a Google service account key
        spreadsheet_id:   the ID from the Google Sheets URL
        """
        creds_dict = json.loads(credentials_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        self.client = gspread.authorize(creds)
        self.spreadsheet_id = spreadsheet_id
        self.sheet = self.client.open_by_key(spreadsheet_id)
        self._ensure_tabs()

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def get_published_count(self) -> int:
        ws = self.sheet.worksheet(TAB_FEED)
        records = ws.get_all_records()
        return len([r for r in records if r.get("Status") == "published"])

    def get_recent_posts(self, n: int = 10) -> list:
        """
        Returns list of dicts (newest first) with keys: topic, format, timestamp.
        Used by TopicSelector to determine rotation.
        """
        ws = self.sheet.worksheet(TAB_FEED)
        records = ws.get_all_records()  # list of dicts, row 1 = headers

        # Filter to published rows only, sort newest-first
        published = [
            r for r in records if r.get("Status") == "published"
        ]
        published.sort(key=lambda r: r.get("Timestamp (UTC)", ""), reverse=True)

        return [
            {
                "topic": r["Topic"],
                "format": r["Format"],
                "timestamp": r["Timestamp (UTC)"],
            }
            for r in published[:n]
        ]

    def publish_post(
        self,
        run_id: str,
        topic: str,
        format_type: str,
        content: str,
        score: int,
        infographic_url: str = "",
    ) -> None:
        ws = self.sheet.worksheet(TAB_FEED)
        hyperlink = f'=HYPERLINK("{infographic_url}", "View Infographic")' if infographic_url else ""
        ws.insert_row(
            [
                run_id,
                _utcnow(),
                topic,
                format_type,
                content,
                score,
                "published",
                hyperlink,
            ],
            index=2,
            value_input_option="USER_ENTERED",
        )
        logger.info(f"Published post to Feed tab | run_id={run_id}")

    def log_attempt(
        self,
        run_id: str,
        attempt: int,
        topic: str,
        format_type: str,
        content: str,
        guardrail_result: dict,
    ) -> None:
        ws = self.sheet.worksheet(TAB_LOG)
        ws.append_row(
            [
                run_id,
                _utcnow(),
                attempt,
                topic,
                format_type,
                content,
                guardrail_result.get("score", 0),
                str(guardrail_result.get("pass", False)),
                ", ".join(guardrail_result.get("flags", [])),
                guardrail_result.get("reason", ""),
            ],
            value_input_option="RAW",
        )

    def log_skip(self, run_id: str, topic: str, format_type: str, reason: str) -> None:
        ws = self.sheet.worksheet(TAB_FEED)
        ws.append_row(
            [run_id, _utcnow(), topic, format_type, "", 0, f"SKIPPED: {reason}"],
            value_input_option="RAW",
        )
        logger.warning(f"Cycle skipped | run_id={run_id} | reason={reason}")

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _ensure_tabs(self) -> None:
        """Create required tabs with headers if they don't exist yet."""
        existing = [ws.title for ws in self.sheet.worksheets()]

        if TAB_FEED not in existing:
            ws = self.sheet.add_worksheet(title=TAB_FEED, rows=1000, cols=10)
            ws.append_row(FEED_HEADERS)
            self._format_header_row(ws)
            logger.info(f"Created tab: {TAB_FEED}")
        else:
            ws = self.sheet.worksheet(TAB_FEED)
            if "Infographic URL" not in ws.row_values(1):
                ws.update_cell(1, len(FEED_HEADERS), "Infographic URL")

        if TAB_LOG not in existing:
            ws = self.sheet.add_worksheet(title=TAB_LOG, rows=2000, cols=12)
            ws.append_row(LOG_HEADERS)
            self._format_header_row(ws)
            logger.info(f"Created tab: {TAB_LOG}")


    def _format_header_row(self, ws) -> None:
        """Bold the header row."""
        try:
            ws.format("1:1", {"textFormat": {"bold": True}})
        except Exception:
            pass  # formatting is cosmetic, never block on it


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
