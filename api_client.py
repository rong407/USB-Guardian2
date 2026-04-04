import requests

#SERVER_URL = "http://127.0.0.1:8000/search"
SERVER_URL = "http://104.218.52.181:8000/search"

def search_by_hash(file_hash):

    try:
        r = requests.get(SERVER_URL, params={"hash": file_hash}, timeout=3)
        return r.json()
    except Exception as e:
        print("API error:", e)
        return None
