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
