import logging
from functools import reduce
from . import ViGEmClient as vigem


logger = logging.getLogger('J2DX.Windows')


BUTTONS = {
	'main-button': vigem.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE,
	'back-button': vigem.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
	'start-button': vigem.XUSB_BUTTON.XUSB_GAMEPAD_START,
	'left-stick-press': vigem.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
	'right-stick-press': vigem.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
	'left-bumper': vigem.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
	'right-bumper': vigem.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
	'up-button': vigem.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
	'right-button': vigem.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
	'down-button': vigem.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
	'left-button': vigem.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
	'y-button': vigem.XUSB_BUTTON.XUSB_GAMEPAD_Y,
	'x-button': vigem.XUSB_BUTTON.XUSB_GAMEPAD_X,
	'a-button': vigem.XUSB_BUTTON.XUSB_GAMEPAD_A,
	'b-button': vigem.XUSB_BUTTON.XUSB_GAMEPAD_B,
}


TRIGGERS = {
	'left-trigger': 'bLeftTrigger',
	'right-trigger': 'bRightTrigger',
}


AXES_VERTICAL = {
	'left-stick-Y': 'sThumbLY',
	'right-stick-Y': 'sThumbRY',
}


AXES_HORIZONTAL = {
	'left-stick-X': 'sThumbLX',
	'right-stick-X': 'sThumbRX',
}


class Device(object):

	def __init__(self, device, addr):
		self.device = device
		self.address = addr
		self._client = vigem.alloc()
		self._target = vigem.target_x360_alloc()
		self._button = set()
		self._report = vigem.XUSB_REPORT(
			wButtons=0,
			bLeftTrigger=0,
			bRightTrigger=0,
			sThumbLX=0,
			sThumbLY=0,
			sThumbRX=0,
			sThumbRY=0,
		)

		error = vigem.VIGEM_ERRORS(vigem.connect(self._client))
		if error != vigem.VIGEM_ERRORS.VIGEM_ERROR_NONE:
			logger.critical(
				f'Device {self.device} at {self.address}::\
					Connection to ViGEm driver failed::{error.name}')
			raise Exception(error.name)
		error = vigem.VIGEM_ERRORS(vigem.target_add(self._client, self._target))
		if error != vigem.VIGEM_ERRORS.VIGEM_ERROR_NONE:
			logger.critical(
				f'Device {self.device} at {self.address}::\
					Adding target failed::{error.name}')
			raise Exception(error.name)

	def close(self):
		error = vigem.VIGEM_ERRORS(vigem.target_remove(self._client, self._target))
		if error != vigem.VIGEM_ERRORS.VIGEM_ERROR_NONE:
			logger.critical(
				f'Device {self.device} at {self.address}::\
					Removing target failed::{error.name}')
			raise Exception(error.name)
		vigem.target_free(self._target)
		vigem.disconnect(self._client)
		vigem.free(self._client)
		logger.debug(f'Destroyed virtual device for {self.device} at {self.address}')

	def send(self, key, value):
		if key in BUTTONS:
			if value:
				self._button.add(BUTTONS[key])
			else:
				self._button.remove(BUTTONS[key])
		wButtons = reduce(lambda a, b: a | b, self._button, 0)
		self._report.wButtons = wButtons
		logger.debug(f'wButtons::Mask {wButtons}::{[b.name for b in self._button]}')
		if key in TRIGGERS:
			if value:
				setattr(self._report, TRIGGERS[key], vigem.XUSB_TRIGGER_MAX)
				logger.debug(f'{TRIGGERS[key]}::{vigem.XUSB_TRIGGER_MAX}')
			else:
				setattr(self._report, TRIGGERS[key], 0)
				logger.debug(f'{TRIGGERS[key]}::0')
		if key in AXES_HORIZONTAL:
			axis = round(value * vigem.XUSB_THUMB_MAX)
			setattr(self._report, AXES_HORIZONTAL[key], axis)
			logger.debug(f'{AXES_HORIZONTAL[key]}::{axis}')
		elif key in AXES_VERTICAL:
			axis = -round(value * vigem.XUSB_THUMB_MAX)
			setattr(self._report, AXES_VERTICAL[key], axis)
			logger.debug(f'{AXES_VERTICAL[key]}::{axis}')
		error = vigem.VIGEM_ERRORS(
			vigem.target_x360_update(self._client, self._target, self._report))
		if error != vigem.VIGEM_ERRORS.VIGEM_ERROR_NONE:
			logger.error(
				f'Device {self.device} at {self.address}::\
					Updating device state failed::{error.name}')
