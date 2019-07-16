import sys
import logging
import platform
import socket
from argparse import ArgumentParser
import qrcode
from socketio import Server, WSGIApp
from eventlet import wsgi, listen
if platform.system() == "Linux":
	try:
		from lib.nix import X360Device, DS4Device
	except ImportError:
		from src.lib.nix import X360Device, DS4Device
else:
	try:
		from lib.win import X360Device, DS4Device
	except ImportError:
		from src.lib.win import X360Device, DS4Device


parser = ArgumentParser(prog='Joy2DroidX-Server')
parser.add_argument(
	'-H', '--host',
	default=None,
	help='Hostname or IP address server will listen on',
)
parser.add_argument(
	'-p', '--port',
	type=int, default=8013,
	help='Port server will listen on. Defaults to 8013',
)
parser.add_argument(
	'-d', '--debug',
	action='store_true',
	help='Print debug information',
)
args = parser.parse_args()


logging.basicConfig(
	level=logging.DEBUG if args.debug else logging.INFO)
logging.getLogger('engineio.server').setLevel(
	logging.INFO if args.debug else logging.ERROR)
logging.getLogger('socketio.server').setLevel(
	logging.INFO if args.debug else logging.ERROR)
wsgiLogger = logging.getLogger('eventlet.wsgi.server')
wsgiLogger.setLevel(
	logging.INFO if args.debug else logging.ERROR)
logger = logging.getLogger('J2DX.server')


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


CLIENTS = {}
DEVICES = {}


sio = Server(logger=args.debug, engineio_logger=args.debug)
app = WSGIApp(sio)


@sio.event
def connect(sid, environ):
	# DEVICES[sid] = Device(environ['REMOTE_ADDR'])
	CLIENTS[sid] = environ['REMOTE_ADDR']
	logger.info(f'Client connected from {environ["REMOTE_ADDR"]}')
	logger.debug(f'Client {environ["REMOTE_ADDR"]} sessionId: {sid}')


@sio.event
def intro(sid, data):
	if data['id'] == 'x360':
		DEVICES[sid] = X360Device(data['device'], CLIENTS[sid])
	else:
		DEVICES[sid] = DS4Device(data['device'], CLIENTS[sid])
	logger.info(
		f'Created virtual {data["type"]} gamepad for {data["device"]} \
			at {CLIENTS[sid]}')


@sio.event
def input(sid, data):
	logger.debug(f'Received INPUT event::{data["key"]}: {data["value"]}')
	DEVICES[sid].send(data['key'], data['value'])


@sio.event
def disconnect(sid):
	device = DEVICES.pop(sid)
	logger.info(f'Disconnected device {device.device} at {device.address}')
	device.close()


if __name__ == '__main__':
	try:
		host = args.host or default_host()
		sock = listen((host, args.port))
	except PermissionError:
		sys.exit(f'Port {args.port} is not available. \
			Please specify a different port with -p option.')
	logger.info(f'Listening on http://{host}:{args.port}/')
	qr = qrcode.QRCode()
	qr.add_data(f'j2dx://{host}:{args.port}/')
	qr.print_ascii(tty=True)
	wsgi.server(sock, app, log=wsgiLogger, log_output=args.debug, debug=False)
