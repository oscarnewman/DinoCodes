import segno
import datetime
import time
import numpy as np
from PIL import Image


def run():
    timestamp = int(time.time() * 1000)
    frames = []  # type: List[Image]
    for i in range(30):
        salt = "635124"
        id = "53214253214321"

        content = salt + id + str(timestamp)
        print(content)
        timestamp += 100

        qr = segno.make(content, error="M", micro=False)
        fn = f"out/{i}.png"
        img = qr.save(fn, scale=10, light="#ffffff", dark="#8697AC")

        frame = Image.open(fn).convert("P")
        frames.append(frame)

    print(frames)
    frames[0].save(
        "qr.gif",
        # format="GIF",
        append_images=frames[1:],
        save_all=True,
        duration=100,
        loop=0,
    )


if __name__ == "__main__":
    run()
