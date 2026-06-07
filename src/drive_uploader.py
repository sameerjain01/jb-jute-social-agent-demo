"""
drive_uploader.py
-----------------
Uploads infographic PNGs to Google Drive using the existing service account.
Returns a publicly accessible view URL.
"""

import json
import logging

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


class DriveUploader:

    def __init__(self, credentials_json: str):
        creds_data = json.loads(credentials_json)
        creds = Credentials.from_service_account_info(creds_data, scopes=SCOPES)
        self.service = build("drive", "v3", credentials=creds, cache_discovery=False)

    def upload(self, file_path: str, filename: str, folder_id: str = None) -> str:
        """Upload PNG to Drive, make it public. Returns view URL."""
        file_meta = {"name": filename}
        if folder_id:
            file_meta["parents"] = [folder_id]
        media = MediaFileUpload(file_path, mimetype="image/png", resumable=False)

        file = self.service.files().create(
            body=file_meta,
            media_body=media,
            fields="id",
        ).execute()

        file_id = file["id"]

        self.service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()

        url = f"https://drive.google.com/file/d/{file_id}/view"
        logger.info(f"Uploaded to Drive: {url}")
        return url
