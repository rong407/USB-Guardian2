import socket, getpass, datetime, json
from utils import sha256

def create_fingerprint(file_path):

    return {
        "fpid": f"FGP-{int(datetime.datetime.now().timestamp())}",
        "host": socket.gethostname(),
        "user": getpass.getuser(),
        "timestamp": datetime.datetime.now().isoformat(),
        "hash": sha256(file_path),
        "file_name": file_path.split("/")[-1]
    }
