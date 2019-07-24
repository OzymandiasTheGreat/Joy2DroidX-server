import os
import sys
import logging
from subprocess import run


logger = logging.getLogger('J2DX.Linux.Setup')


GROUP = 'j2dx'
UDEV_PATH = '/etc/udev/rules.d/80-j2dx.uinput.rules'
UDEV_RULE = (
	f'SUBSYSTEM=="misc", KERNEL=="uinput", MODE="0660", GROUP="{GROUP}"')


def groupadd():
	proc = run(['groupadd', '-f', GROUP], capture_output=True, text=True)
	if proc.returncode != 0:
		logger.critical(proc.stderr)
		sys.exit(proc.returncode)
	logger.info(proc.stdout)


def usermod(user):
	proc = run(
		['usermod', '-a', '-G', GROUP, user], capture_output=True, text=True)
	if proc.returncode != 0:
		logger.critical(proc.stderr)
		sys.exit(proc.returncode)
	logger.info(proc.stdout)


def setup(user):
	if os.geteuid() != 0:
		logger.critical('Setup needs to run as root.')
		sys.exit('Try running this command with sudo.')

	try:
		with open(os.open(UDEV_PATH, os.O_CREAT | os.O_WRONLY, 0o660), 'w') as fd:
			fd.write(UDEV_RULE)
	except OSError as e:
		logger.critical(e.strerror)
		sys.exit(e.errno)

	groupadd()
	usermod(user)
	logger.info(
		'Setup complete. You may need to reboot for UDEV rules to take effect.')
