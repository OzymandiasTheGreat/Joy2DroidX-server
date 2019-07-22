import sys
import logging
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from ctypes import windll, c_void_p, c_wchar_p, c_int
from .. import VIGEM_URI, VIGEM_REL


SE_ERR_ACCESSDENIED = 5
SUCCESS = lambda errno: errno > 32    # noqa


ShellExecuteW = windll.shell32.ShellExecuteW
ShellExecuteW.argtypes = (
	c_void_p, c_wchar_p, c_wchar_p, c_wchar_p, c_wchar_p, c_int)
ShellExecuteW.restype = c_int


logger = logging.getLogger('J2DX.Windows.Setup')


def setup():
	with NamedTemporaryFile(
			delete=False, prefix='ViGEmBus-', suffix='.exe') as tmp:
		logger.info('Downloading compatible ViGEmBus driver.')
		try:
			resp = urlopen(VIGEM_URI)
			tmp.write(resp.read())
			vigembus = tmp.name
		except OSError as e:
			logger.critical(f'Driver download failed. Error {e.errno}')
			logger.info(
				f'Please manually download latest driver from {VIGEM_REL}')
			sys.exit(e.errno)
	logger.info('Running setup. Please accept UAC prompt when it appears.')
	ret = ShellExecuteW(
		None, 'runas',
		vigembus, '/exenoui /quiet /promptrestart',
		None, 1)
	if SUCCESS(ret):
		logger.info(
			'Setup complete. '
			'You may need to reboot before you can use virtual device driver.')
		sys.exit(0)
	else:
		if ret == SE_ERR_ACCESSDENIED:
			logger.critical('Setup needs administrator access to install drivers.')
		else:
			logger.critical(f'Unexpected error: {ret}')
		sys.exit(ret)
