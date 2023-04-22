import socket

import qrcode

# Get the hostname and IP address of the current machine
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

# Generate a QR code containing the URL for localhost
url = f"http://{ip_address}:8000"
qr = qrcode.QRCode(version=1, box_size=100, border=4)
qr.add_data(url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.show()