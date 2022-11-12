def from_bytes(bytes: int):
    prefix = {0: "B", 1: "kB", 2: "MB", 3: "GB", 4: "TB"}

    n = 0
    while bytes >= 1024:
        bytes /= 1024
        n += 1
    return "{:.2f} {}".format(bytes, prefix[n])
