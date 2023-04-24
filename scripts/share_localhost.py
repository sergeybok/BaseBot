import qrcode
import subprocess
import argparse


ROOT = '/bots'

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=str, default='8000')
parser.add_argument('--bot_name', type=str, default=None)

args = parser.parse_args()
if args.bot_name is not None:
    ROOT = ROOT + '/' + args.bot_name


# Get the hostname and IP (non loopback) address of the current machine
cmd = "ifconfig | grep 'inet ' | grep -Fv 127.0.0.1 | awk '{print $2}'"
output = subprocess.check_output(cmd, shell=True)
ip_address = output.decode().strip()

# Generate a QR code containing the URL for localhost
url = f"http://{ip_address}:{args.port}/{ROOT}"
print('\t Your Local Network URL: ', url)
qr = qrcode.QRCode(version=1, box_size=100, border=4)
qr.add_data(url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.show()