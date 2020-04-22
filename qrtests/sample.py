from PIL import Image
from pyzbar.pyzbar import decode
import pyqrcode
import time
import os

FNAME = './sample.png'

# if os.path.exists(FNAME):
#     os.remove(FNAME)

# ENCODE

time_before_encode = time.time() * 1000
qr = pyqrcode.create(time.time())
qr.png(FNAME)
encode_time = time.time() * 1000 - time_before_encode

# DECODE
time_before_decode = time.time() * 1000
img = Image.open(FNAME)
decoded = decode(img)
decode_time = time.time() * 1000 - time_before_decode

print("Encode time:", encode_time)
print("Decode time:", decode_time)

print(decoded)
