import logging
from evdev import UInput, AbsInfo, ecodes as e


logger = logging.getLogger('J2DX.Linux')


CAPABILITIES = {
	e.EV_KEY: [
		e.BTN_Y,
		e.BTN_X,
		e.BTN_A,
		e.BTN_B,
		e.BTN_THUMBL,
		e.BTN_THUMBR,
		e.BTN_SELECT,
		e.BTN_START,
		e.BTN_MODE,
		e.BTN_TRIGGER_HAPPY1,
		e.BTN_TRIGGER_HAPPY2,
		e.BTN_TRIGGER_HAPPY3,
		e.BTN_TRIGGER_HAPPY4,
		e.BTN_TL,
		e.BTN_TL2,
		e.BTN_TR,
		e.BTN_TR2,
	],
	e.EV_ABS: [
		(e.ABS_X, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
		(e.ABS_Y, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
		(e.ABS_RX, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
		(e.ABS_RY, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
	],
}


BUTTONS = {
	'main-button': e.BTN_MODE,
	'back-button': e.BTN_SELECT,
	'start-button': e.BTN_START,
	'left-stick-press': e.BTN_THUMBL,
	'right-stick-press': e.BTN_THUMBR,
	'left-bumper': e.BTN_TL,
	'left-trigger': e.BTN_TL2,
	'right-bumper': e.BTN_TR,
	'right-trigger': e.BTN_TR2,
	'up-button': e.BTN_TRIGGER_HAPPY3,
	'right-button': e.BTN_TRIGGER_HAPPY2,
	'down-button': e.BTN_TRIGGER_HAPPY4,
	'left-button': e.BTN_TRIGGER_HAPPY1,
	'y-button': e.BTN_Y,
	'x-button': e.BTN_X,
	'a-button': e.BTN_A,
	'b-button': e.BTN_B,
}


AXES = {
	'left-stick-X': e.ABS_X,
	'left-stick-Y': e.ABS_Y,
	'right-stick-X': e.ABS_RX,
	'right-stick-Y': e.ABS_RY,
}


class Device(object):

	def __init__(self, device, addr):
		self.device = device
		self.address = addr
		self._ui = UInput(
			CAPABILITIES, name='Joy2DroidX-Virtual-Gamepad', version=0x1)

	def close(self):
		self._ui.close()
		logger.debug(f'Destroyed virtual device for {self.device} at {self.address}')

	def send(self, key, value):
		if key in BUTTONS:
			logger.debug(f'Sending button event::{e.keys[BUTTONS[key]]}: {value}')
			self._ui.write(e.EV_KEY, BUTTONS[key], value)
			self._ui.syn()
		elif key in AXES:
			coord = round(127 * value) + 127
			logger.debug(f'Sending axis event::{e.ABS[AXES[key]]}: {coord}')
			self._ui.write(e.EV_ABS, AXES[key], coord)
			self._ui.syn()
