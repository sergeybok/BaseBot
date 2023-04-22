import qrcode
import subprocess

# Get the hostname and IP (non loopback) address of the current machine
cmd = "ifconfig | grep 'inet ' | grep -Fv 127.0.0.1 | awk '{print $2}'"
output = subprocess.check_output(cmd, shell=True)
ip_address = output.decode().strip()

# Generate a QR code containing the URL for localhost
url = f"http://{ip_address}:8000"
qr = qrcode.QRCode(version=1, box_size=100, border=4)
qr.add_data(url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.show()