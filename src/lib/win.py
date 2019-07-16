import logging
from abc import ABC, abstractmethod
from functools import reduce
from . import ViGEmClient as vigem


logger = logging.getLogger('J2DX.Windows')


class Device(ABC):

	@abstractmethod
	def __init__(self, device, addr):
		self.device = device
		self.address = addr
		self._client = vigem.alloc()

	def _create_device(self):
		error = vigem.VIGEM_ERRORS(vigem.connect(self._client))
		if error != vigem.VIGEM_ERRORS.VIGEM_ERROR_NONE:
			logger.critical(
				f'Virtual {self.type} device {self.device} at {self.address}::\
					Connection to ViGEm driver failed::{error.name}')
			raise Exception(error.name)
		error = vigem.VIGEM_ERRORS(vigem.target_add(self._client, self._target))
		if error != vigem.VIGEM_ERRORS.VIGEM_ERROR_NONE:
			logger.critical(
				f'Virtual {self.type} device {self.device} at {self.address}::\
					Adding target failed::{error.name}')
			raise Exception(error.name)

	def close(self):
		error = vigem.VIGEM_ERRORS(vigem.target_remove(self._client, self._target))
		if error != vigem.VIGEM_ERRORS.VIGEM_ERROR_NONE:
			logger.critical(
				f'Virtual {self.type} device {self.device} at {self.address}::\
					Removing target failed::{error.name}')
			raise Exception(error.name)
		vigem.target_free(self._target)
		vigem.disconnect(self._client)
		vigem.free(self._client)
		logger.debug(
			f'Destroyed virtual {self.type} device for {self.device} \
				at {self.address}')

	@abstractmethod
	def send(self, key, value):
		pass


class X360Device(Device):

	buttons = {
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
	triggers = {
		'left-trigger': 'bLeftTrigger',
		'right-trigger': 'bRightTrigger',
	}
	axes_vertical = {
		'left-stick-Y': 'sThumbLY',
		'right-stick-Y': 'sThumbRY',
	}
	axes_horizontal = {
		'left-stick-X': 'sThumbLX',
		'right-stick-X': 'sThumbRX',
	}

	def __init__(self, device, addr):
		super().__init__(device, addr)
		self.type = "Xbox 360 Controller"
		self._target = vigem.target_x360_alloc()
		self._wButtons = set()
		self._report = vigem.XUSB_REPORT(
			wButtons=0,
			bLeftTrigger=0,
			bRightTrigger=0,
			sThumbLX=0,
			sThumbLY=0,
			sThumbRX=0,
			sThumbRY=0,
		)
		self._create_device()

	def send(self, key, value):
		if key in self.buttons:
			if value:
				self._wButtons.add(self.buttons[key])
			else:
				self._wButtons.remove(self.buttons[key])
		elif key in self.triggers:
			if value:
				setattr(self._report, self.triggers[key], vigem.XUSB_TRIGGER_MAX)
				logger.debug(f'{self.triggers[key]}::{vigem.XUSB_TRIGGER_MAX}')
			else:
				setattr(self._report, self.triggers[key], 0)
				logger.debug(f'{self.triggers[key]}::0')
		elif key in self.axes_vertical:
			axis = -round(value * vigem.XUSB_THUMB_MAX)
			setattr(self._report, self.axes_vertical[key], axis)
			logger.debug(f'{self.axes_vertical[key]}::{axis}')
		elif key in self.axes_horizontal:
			axis = round(value * vigem.XUSB_THUMB_MAX)
			setattr(self._report, self.axes_horizontal[key], axis)
			logger.debug(f'{self.axes_horizontal[key]}::{axis}')
		wButtons = reduce(lambda a, b: a | b, self._wButtons, 0)
		self._report.wButtons = wButtons
		logger.debug(
			f'wButtons::Mask {wButtons}::{[b.name for b in self._wButtons]}')
		error = vigem.VIGEM_ERRORS(
			vigem.target_x360_update(self._client, self._target, self._report)
		)
		if error != vigem.VIGEM_ERRORS.VIGEM_ERROR_NONE:
			logger.error(
				f'Virtual {self.type} device {self.device} at {self.address}::\
					Updating device state failed::{error.name}'
			)


class DS4Device(Device):

	buttons = {
		'back-button': vigem.DS4_BUTTONS.DS4_BUTTON_SHARE,
		'start-button': vigem.DS4_BUTTONS.DS4_BUTTON_OPTIONS,
		'left-stick-press': vigem.DS4_BUTTONS.DS4_BUTTON_THUMB_LEFT,
		'right-stick-press': vigem.DS4_BUTTONS.DS4_BUTTON_THUMB_RIGHT,
		'left-bumper': vigem.DS4_BUTTONS.DS4_BUTTON_SHOULDER_LEFT,
		'right-bumper': vigem.DS4_BUTTONS.DS4_BUTTON_SHOULDER_RIGHT,
		'y-button': vigem.DS4_BUTTONS.DS4_BUTTON_TRIANGLE,
		'x-button': vigem.DS4_BUTTONS.DS4_BUTTON_SQUARE,
		'a-button': vigem.DS4_BUTTONS.DS4_BUTTON_CROSS,
		'b-button': vigem.DS4_BUTTONS.DS4_BUTTON_CIRCLE,
	}
	specials = {
		'main-button': vigem.DS4_SPECIAL_BUTTONS.DS4_SPECIAL_BUTTON_PS,
	}
	dpad = {
		'up-button': vigem.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH,
		'right-button': vigem.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_EAST,
		'down-button': vigem.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH,
		'left-button': vigem.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST,
	}
	triggers = {
		'left-trigger': ('bTriggerL', vigem.DS4_BUTTONS.DS4_BUTTON_TRIGGER_LEFT),
		'right-trigger': ('bTriggerR', vigem.DS4_BUTTONS.DS4_BUTTON_TRIGGER_RIGHT),
	}
	axes_vertical = {
		'left-stick-Y': 'bThumbLY',
		'right-stick-Y': 'bThumbRY',
	}
	axes_horizontal = {
		'left-stick-X': 'bThumbLX',
		'right-stick-X': 'bThumbRX',
	}

	def __init__(self, device, addr):
		super().__init__(device, addr)
		self.type = "Sony Computer Entertainment Wireless Controller"
		self._target = vigem.target_ds4_alloc()
		self._wButtons = set()
		self._report = vigem.DS4_REPORT(
			bThumbLX=0,
			bThumbLY=0,
			bThumbRX=0,
			bThumbRY=0,
			wButtons=0,
			bSpecial=0,
			bTriggerL=0,
			bTriggerR=0,
		)
		vigem.DS4_REPORT_INIT(self._report)
		self._create_device()

	def send(self, key, value):
		self._report.wButtons = 0
		if key in self.buttons:
			if value:
				self._wButtons.add(self.buttons[key])
			else:
				self._wButtons.remove(self.buttons[key])
		elif key in self.specials:
			if value:
				self._report.bSpecial |= self.specials[key]
				logger.debug(f'{self.specials[key].name}::{self.specials[key]}')
			else:
				self._report.bSpecial = 0
				logger.debug(f'{self.specials[key].name}::0')
		elif key in self.dpad:
			if value:
				vigem.DS4_SET_DPAD(self._report, self.dpad[key])
				logger.debug(f'{self.dpad[key].name}')
			else:
				vigem.DS4_SET_DPAD(
					self._report, vigem.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
				logger.debug(f'{vigem.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE.name}')
		elif key in self.triggers:
			if value:
				setattr(self._report, self.triggers[key][0], vigem.XUSB_TRIGGER_MAX)
				logger.debug(f'{self.triggers[key][0]}::{vigem.XUSB_TRIGGER_MAX}')
				self._wButtons.add(self.triggers[key][1])
			else:
				setattr(self._report, self.triggers[key][0], 0)
				logger.debug(f'{self.triggers[key][0]}::0')
				self._wButtons.remove(self.triggers[key][1])
		elif key in self.axes_vertical:
			axis = round(value * 127) + 127
			setattr(self._report, self.axes_vertical[key], axis)
			logger.debug(f'{self.axes_vertical[key]}::{axis}')
		elif key in self.axes_horizontal:
			axis = round(value * 127) + 127
			setattr(self._report, self.axes_horizontal[key], axis)
			logger.debug(f'{self.axes_horizontal[key]}::{axis}')
		self._report.wButtons |= reduce(lambda a, b: a | b, self._wButtons, 0)
		logger.debug(
			f'wButtons::Mask {self._report.wButtons}::\
				{[b.name for b in self._wButtons]}')
		error = vigem.VIGEM_ERRORS(
			vigem.target_ds4_update(self._client, self._target, self._report)
		)
		if error != vigem.VIGEM_ERRORS.VIGEM_ERROR_NONE:
			logger.error(
				f'Virtual {self.type} device {self.device} at {self.address}::\
					Updating device state failed::{error.name}'
			)
