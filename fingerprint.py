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
