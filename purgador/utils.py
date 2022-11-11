from datetime import datetime

prefix = {1: "kB", 2: "MB", 3: "GB", 4: "TB"}
def from_bytes(bytes: int):
    n = 0
    while (bytes >= 1024):
        bytes /= 1024
        n += 1
    return "{:.2f} {}".format(bytes, prefix[n])

def timestamp(b):
    dt = datetime.utcnow()
    seconds = dt.timestamp()
    uptime = seconds - b
    return "<t:{}:R>".format(int(uptime))