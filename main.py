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
