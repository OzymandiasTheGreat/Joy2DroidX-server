import os
import sys
import logging
import platform
import socket
from argparse import ArgumentParser
import qrcode
from socketio import Server, WSGIApp
from eventlet import wsgi, listen
if platform.system() == 'Linux':
	try:
		from .nix.device import X360Device, DS4Device
		from .nix.setup import setup
	except ImportError:
		from j2dx.nix.device import X360Device, DS4Device
		from j2dx.nix.setup import setup
else:
	try:
		from .win.device import X360Device, DS4Device
		from .win.setup import setup
	except ImportError:
		from j2dx.win.device import X360Device, DS4Device
		from j2dx.win.setup import setup


def parse_args():
	parser = ArgumentParser()
	if platform.system() == 'Linux':
		parser.add_argument(
			'user',
			nargs='?',
			default=os.getenv('SUDO_USER'),
			help='Only used with --setup. User to configure for UInput access.'
		)
	parser.add_argument(
		'-s', '--setup',
		action='store_true',
		help='Setup system for virtual device creation.'
		'Must have root/administrator access.',
	)
	parser.add_argument(
		'-H', '--host',
		default=None,
		help='Hostname or IP address the server will listen on.',
	)
	parser.add_argument(
		'-p', '--port',
		type=int, default=8013,
		help='Port the server will listen on. Defaults to 8013.',
	)
	parser.add_argument(
		'-d', '--debug',
		action='store_true',
		help='Print debug information.',
	)
	return parser.parse_args()


def get_logger(debug):
	logging.basicConfig(
		level=logging.DEBUG if debug else logging.INFO)
	logging.getLogger('engineio.server').setLevel(
		logging.INFO if debug else logging.ERROR)
	logging.getLogger('socketio.server').setLevel(
		logging.INFO if debug else logging.ERROR)
	wsgi_logger = logging.getLogger('eventlet.wsgi.server')
	wsgi_logger.setLevel(
		logging.INFO if debug else logging.ERROR)
	return (logging.getLogger('J2DX.server'), wsgi_logger)


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


def main():
	args   = parse_args()
	logger, wsgi_logger = get_logger(args.debug)

	if args.setup:
		if platform.system() == 'Linux':
			setup(args.user)
		else:
			setup()
		sys.exit(0)
		return

	CLIENTS = {}
	DEVICES = {}

	sio = Server(logger=args.debug, engineio_logger=args.debug)
	app = WSGIApp(sio)

	@sio.event
	def connect(sid, environ):
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
			f'Created virtual {data["type"]} gamepad for {data["device"]} '
			f'at {CLIENTS[sid]}')

	@sio.event
	def input(sid, data):
		logger.debug(f'Received INPUT event::{data["key"]}: {data["value"]}')
		DEVICES[sid].send(data['key'], data['value'])

	@sio.event
	def disconnect(sid):
		device = DEVICES.pop(sid)
		logger.info(f'Disconnected device {device.device} at {device.address}')
		device.close()

	try:
		host = args.host or default_host()
		sock = listen((host, args.port))
	except PermissionError:
		sys.exit(
			f'Port {args.port} is not available. '
			f'Please specify a different port with -p option.'
		)
	logger.info(f'Listening on http://{host}:{args.port}/')
	qr = qrcode.QRCode()
	qr.add_data(f'j2dx://{host}:{args.port}/')
	if platform.system() == 'Windows':
		import colorama
		colorama.init()
	qr.print_ascii(tty=True)
	wsgi.server(sock, app, log=wsgi_logger, log_output=args.debug, debug=False)


if __name__ == '__main__':
	main()
