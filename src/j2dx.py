import logging
import platform
import socket
import argparse
import qrcode
from socketio import Server, WSGIApp
from eventlet import wsgi, listen
if platform.system() == "Linux":
	try:
		from lib.nix import Device
	except ImportError:
		from src.lib.nix import Device
else:
	try:
		from lib.win import Device
	except ImportError:
		from src.lib.win import Device


# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


DEVICES = {}
DEFAULT_PORT = 8013


def default_host():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		sock.connect(('1.255.255.255', 1))
		IP = sock.getsockname()[0]
	except IndexError:
		IP = '127.0.0.1'
	finally:
		sock.close()
	return IP


sio = Server()
app = WSGIApp(sio)


@sio.event
def connect(sid, environ):
	DEVICES[sid] = Device(environ['REMOTE_ADDR'])


@sio.event
def input(sid, data):
	DEVICES[sid].send(data['key'], data['value'])


@sio.event
def disconnect(sid):
	device = DEVICES.pop(sid)
	logger.error(f'Deleting device {device.ip}')
	device.close()


if __name__ == '__main__':
	qr = qrcode.QRCode()
	qr.add_data(f'j2dx://{IP}:{PORT}/')
	qr.print_ascii(tty=True)
	wsgi.server(listen((IP, PORT)), app)
