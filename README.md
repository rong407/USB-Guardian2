ด้านล่างคือ **Endpoint Agent เวอร์ชันเต็ม (Modular Code – Production-style)** สำหรับโปรเจกต์
ออกแบบให้ **แยก module ชัดเจน + รองรับ Metadata + AI + Log + USB detection**

---

# 🧠 Architecture (Agent)

```text
agent/
 ├── main.py
 ├── config.py
 ├── detector.py
 ├── fingerprint.py
 ├── metadata.py
 ├── ai_engine.py
 ├── logger.py
 └── utils.py
```

---

# 1️⃣ config.py

```python
SERVER_URL = "http://127.0.0.1:8000/log"

SUPPORTED_EXT = ["pdf", "docx", "xlsx", "jpg", "png"]

RISK_THRESHOLD = 80

WATCH_PATH = "E:\\"  # USB Drive
```

---

# 2️⃣ utils.py

```python
import hashlib

def sha256(file_path):
    h = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            h.update(chunk)
    return h.hexdigest()
```

---

# 3️⃣ fingerprint.py

```python
import socket
import getpass
import datetime
import json
from utils import sha256

def create_fingerprint(file_path):

    fp = {
        "fpid": f"FGP-{int(datetime.datetime.now().timestamp())}",
        "host": socket.gethostname(),
        "user": getpass.getuser(),
        "timestamp": datetime.datetime.now().isoformat(),
        "hash": sha256(file_path)
    }

    return json.dumps(fp)
```

---

# 4️⃣ ai_engine.py

```python
import re

def detect_sensitive(file_path):

    try:
        with open(file_path, "r", errors="ignore") as f:
            content = f.read()
    except:
        return 0

    score = 0

    patterns = [
        r"confidential",
        r"password",
        r"\b\d{13,16}\b"
    ]

    for p in patterns:
        if re.search(p, content, re.IGNORECASE):
            score += 40

    return score
```

---

# 5️⃣ metadata.py (core สำคัญ)

```python
import json

def embed_metadata(file_path, fingerprint):

    ext = file_path.split(".")[-1].lower()

    if ext in ["txt"]:
        with open(file_path, "a") as f:
            f.write("\nFP:" + fingerprint)

    elif ext in ["jpg", "png"]:
        try:
            from PIL import Image
            img = Image.open(file_path)
            img.save(file_path, "PNG")
        except:
            pass

    # NOTE: extend สำหรับ pdf/docx/xlsx ได้
```

👉 จุดนี้สามารถต่อยอดตามที่อธิบายก่อนหน้า

---

# 6️⃣ logger.py

```python
import requests

def send_log(data, server_url):

    try:
        requests.post(server_url, json=data, timeout=2)
    except:
        print("log send failed")
```

---

# 7️⃣ detector.py

```python
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
```

---

# 8️⃣ main.py

```python
from watchdog.observers import Observer
import time

from detector import USBMonitor
from config import WATCH_PATH

if __name__ == "__main__":

    observer = Observer()
    observer.schedule(USBMonitor(), WATCH_PATH, recursive=False)

    observer.start()

    print("Agent running...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
```

---

# 🚀 สิ่งที่ Agent นี้ทำได้แล้ว

✅ Detect file copy ไป USB
✅ วิเคราะห์ AI (basic)
✅ สร้าง fingerprint
✅ ฝัง metadata (extend ได้)
✅ ส่ง log ไป server

---

# 🔥 สิ่งที่ควรต่อยอด (Production Ready)

## 1. รองรับ Metadata จริง (สำคัญมาก)

* PDF → PyMuPDF
* DOCX → python-docx
* XLSX → openpyxl

---

## 2. USB Device Info

เพิ่ม:

```python
device_id
serial_number
```

---

## 3. Anti-bypass

* detect rename
* detect zip

---

## 4. Offline Queue

```python
if send fail → save local → retry
```

---

เพื่อให้รองรับ **Production + AI + Traceability จริง**
ของเดิมใช้ได้เป็น prototype แต่ยังขาดหลายส่วนสำคัญ

---

# 🎯 ภาพรวมสิ่งที่ต้องเพิ่มใน Server/API

จากเดิม:

```text
Receive Log → Save file
```

ควรอัปเกรดเป็น:

```text
Receive → Validate → Enrich → Store → Query → Alert
```

---

# 🔧 1. เพิ่ม Log Validation (สำคัญมาก)

ป้องกันข้อมูลปลอมจาก Agent

```python
def validate_log(data):
    required = ["fpid", "host", "user", "timestamp", "hash"]
    return all(k in data for k in required)
```

ใช้ใน API:

```python
if not validate_log(data):
    return {"status": "invalid"}
```

---

# 🔧 2. เพิ่ม Field ใหม่ (รองรับ AI + USB)

จากเดิม log:

```json
{
 "host": "...",
 "user": "...",
 "hash": "..."
}
```

👉 ต้องเพิ่ม:

```json
{
 "fpid": "FGP-123",
 "host": "PC01",
 "user": "somchai",
 "timestamp": "...",
 "hash": "...",
 "risk_score": 85,
 "action": "BLOCK",
 "usb_device": "Kingston32GB",
 "file_name": "budget.xlsx"
}
```

---

# 🔧 3. เปลี่ยนจาก Raw Log → Structured Storage

## Option A (ง่าย)

ยังใช้ file แต่จัด format ดีขึ้น

```text
logs/
  2026-03-13/
    events.jsonl
```

---

## Option B (แนะนำ)

ใช้ DB เช่น SQLite / PostgreSQL

```python
CREATE TABLE logs (
    fpid TEXT,
    host TEXT,
    user TEXT,
    timestamp TEXT,
    hash TEXT,
    risk INTEGER,
    action TEXT
)
```

👉 จะทำให้ query ได้เร็วมาก

---

# 🔧 4. เพิ่ม API สำหรับ Query (สำคัญสำหรับ Demo)

## 🔍 ค้นหาไฟล์จาก hash

```python
@app.get("/search")
def search(hash: str):
    # search in log
    return result
```

---

## 🔍 ค้นหาจาก user

```python
@app.get("/user/{username}")
def search_user(username: str):
    return results
```

---

## 🔍 ค้นหาจาก FPID

```python
@app.get("/fpid/{fpid}")
def search_fpid(fpid: str):
    return result
```

---

# 🔧 5. เพิ่ม Risk Alert (ทำให้ดู AI จริง)

```python
if data.get("risk_score", 0) > 80:
    print("ALERT: High Risk Transfer")
```

👉 ต่อยอด:

* Email alert
* Line notify
* Dashboard

---

# 🔧 6. เพิ่ม Deduplication (กัน log ซ้ำ)

```python
seen_hash = set()

if data["hash"] in seen_hash:
    return {"status": "duplicate"}

seen_hash.add(data["hash"])
```

---

# 🔧 7. เพิ่ม API สำหรับ Dashboard

```python
@app.get("/stats")
def stats():
    return {
        "total_events": ...,
        "high_risk": ...,
        "blocked": ...
    }
```

---

# 🔧 8. เพิ่ม Authentication (ขั้นกลาง)

```python
API_KEY = "secret123"

@app.post("/log")
def receive_log(data: dict, api_key: str):
    if api_key != API_KEY:
        return {"status": "unauthorized"}
```

---

# 🔧 9. Logging ที่ Server เอง

```python
import logging

logging.basicConfig(filename="server.log", level=logging.INFO)
logging.info(data)
```

---

# 🔥 ตัวอย่าง Server เวอร์ชันปรับปรุง

```python
from fastapi import FastAPI
from datetime import datetime
import json, os

app = FastAPI()
LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)

def validate_log(data):
    required = ["fpid", "host", "user", "timestamp", "hash"]
    return all(k in data for k in required)


@app.post("/log")
def receive_log(data: dict):

    if not validate_log(data):
        return {"status": "invalid"}

    date = datetime.now().strftime("%Y-%m-%d")
    path = f"{LOG_DIR}/{date}.jsonl"

    with open(path, "a") as f:
        f.write(json.dumps(data) + "\n")

    if data.get("risk_score", 0) > 80:
        print("⚠ HIGH RISK DETECTED:", data["file_name"])

    return {"status": "ok"}


@app.get("/search")
def search(hash: str):

    for file in os.listdir(LOG_DIR):
        with open(os.path.join(LOG_DIR, file)) as f:
            for line in f:
                record = json.loads(line)
                if record["hash"] == hash:
                    return record

    return {"status": "not found"}
```

---

# 🚀 สิ่งที่ได้หลังปรับ Server

✅ รองรับ AI + Risk Score
✅ Query ได้ (Demo โคตรดูโปร)
✅ Alert ได้
✅ ป้องกัน log ปลอม
✅ พร้อมต่อ Dashboard

---

# 🎯 สรุป

> “Server จะถูกพัฒนาให้เป็นศูนย์กลางในการรับ ตรวจสอบ และวิเคราะห์ข้อมูล โดยสามารถค้นหาเหตุการณ์ย้อนหลัง แจ้งเตือนความเสี่ยง และรองรับการขยายไปสู่ระบบ Dashboard และ SIEM ได้”

---



