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
