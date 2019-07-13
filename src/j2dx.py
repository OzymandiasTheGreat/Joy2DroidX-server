import logging
import socket
import qrcode
from socketio import Server, WSGIApp
from eventlet import wsgi, listen
from nix import Device


# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


DEVICES = {}


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
	sock.connect(('1.255.255.255', 1))
	IP = sock.getsockname()[0]
except IndexError:
	IP = '127.0.0.1'
finally:
	sock.close()
PORT = 8013


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
	device._ui.close()


if __name__ == '__main__':
	qr = qrcode.QRCode()
	qr.add_data(f'j2dx://{IP}:{PORT}/')
	qr.print_ascii(tty=True)
	wsgi.server(listen((IP, PORT)), app)
