from watchdog.events import FileSystemEventHandler
import os
import json

from fingerprint import create_fingerprint
from metadata import embed_metadata
from logger import send_log
from ai_engine import detect_sensitive
from config import SERVER_URL, SUPPORTED_EXT, RISK_THRESHOLD

class USBMonitor(FileSystemEventHandler):

    def on_created(self, event):

        if event.is_directory:
            return

        path = event.src_path
        ext = path.split(".")[-1].lower()

        if ext not in SUPPORTED_EXT:
            return

        print("Detected:", path)

        # 1. AI Detection
        risk = detect_sensitive(path)

        # 2. Create fingerprint
        fp = create_fingerprint(path)

        # 3. Decision
        if risk > RISK_THRESHOLD:
            print("BLOCKED:", path)
            return

        # 4. Embed metadata
        embed_metadata(path, fp)

        # 5. Send log
        send_log(json.loads(fp), SERVER_URL)
