

from datetime import datetime, UTC


def log(message):
    timestamp = datetime.now(UTC).strftime("%H:%M:%S.%f")
    print(f"[{timestamp}] {message}")