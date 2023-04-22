import os
import socket

import qrcode
from ascii_magic import AsciiArt
from PIL import ImageOps

# Get the hostname and IP address of the current machine
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

# Generate a QR code containing the URL for localhost
url = f"http://{ip_address}:8000"
qr = qrcode.QRCode(version=1, box_size=10, border=4)
qr.add_data(url)
qr.make(fit=True)
img = qr.make_image(fill_color="yellow", back_color="blue")
img.save("localhost.jpg")

# Convert the QR code image to ASCII art
my_art = AsciiArt.from_image("localhost.jpg")
my_art.to_terminal(columns=100)

# Remove the QR code image
os.remove("localhost.jpg")