import requests

def send_log(data, server_url):

    try:
        requests.post(server_url, json=data, timeout=2)
    except:
        print("log send failed")
