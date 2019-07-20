import logging
from abc import ABC, abstractmethod
from evdev import UInput, AbsInfo, ecodes as e


logger = logging.getLogger('J2DX.Linux')


class Device(ABC):

	@abstractmethod
	def __init__(self, device, addr):
		self.device = device
		self.address = addr

	def close(self):
		self._ui.close()
		logger.debug(
			f'Destroyed virtual {self.type} device for {self.device} \
				at {self.address}')

	@abstractmethod
	def send(self, key, value):
		pass


class X360Device(Device):

	capabilities = {
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
	buttons = {
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
	axes = {
		'left-stick-X': e.ABS_X,
		'left-stick-Y': e.ABS_Y,
		'right-stick-X': e.ABS_RX,
		'right-stick-Y': e.ABS_RY,
	}

	def __init__(self, device, addr):
		super().__init__(device, addr)
		self.type = "Xbox 360 Controller"
		self._ui = UInput(
			events=self.capabilities,
			name=self.type,
			vendor=0x045e,
			product=0x028e,
			version=0x0110,
			bustype=e.BUS_USB,
		)

	def send(self, key, value):
		if key in self.buttons:
			logger.debug(f'Sending button event::{e.keys[self.buttons[key]]}: {value}')
			self._ui.write(e.EV_KEY, self.buttons[key], value)
			self._ui.syn()
		elif key in self.axes:
			coord = round(127 * value) + 127
			logger.debug(f'Sending axis event::{e.ABS[self.axes[key]]}: {coord}')
			self._ui.write(e.EV_ABS, self.axes[key], coord)
			self._ui.syn()


class DS4Device(Device):

	capabilities = {
		e.EV_KEY: [
			e.BTN_WEST,    # Square
			e.BTN_SOUTH,   # Cross
			e.BTN_EAST,    # Circle
			e.BTN_NORTH,   # Triangle
			e.BTN_TL,      # L1
			e.BTN_TR,      # R1
			e.BTN_TL2,     # L2
			e.BTN_TR2,     # R2
			e.BTN_SELECT,  # Share
			e.BTN_START,   # Options
			e.BTN_THUMBL,  # L3
			e.BTN_THUMBR,  # R3
			e.BTN_MODE,    # PS
		],
		e.EV_ABS: [
			(e.ABS_X, AbsInfo(
				value=0, min=0, max=255, fuzz=0, flat=5, resolution=0)),
			(e.ABS_Y, AbsInfo(
				value=0, min=0, max=255, fuzz=0, flat=5, resolution=0)),
			# right stick X
			(e.ABS_RX, AbsInfo(
				value=0, min=0, max=255, fuzz=0, flat=5, resolution=0)),
			# right stick Y
			(e.ABS_RY, AbsInfo(
				value=0, min=0, max=255, fuzz=0, flat=5, resolution=0)),
			# L2
			(e.ABS_Z, AbsInfo(
				value=0, min=0, max=255, fuzz=0, flat=5, resolution=0)),
			# R2
			(e.ABS_RZ, AbsInfo(
				value=0, min=0, max=255, fuzz=0, flat=5, resolution=0)),
			# dpad_left, dpad_right
			(e.ABS_HAT0X, AbsInfo(
				value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
			# dpad_up, dpad_down
			(e.ABS_HAT0Y, AbsInfo(
				value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
		]
	}
	buttons = {
		'main-button': e.BTN_MODE,
		'back-button': e.BTN_SELECT,
		'start-button': e.BTN_START,
		'left-stick-press': e.BTN_THUMBL,
		'right-stick-press': e.BTN_THUMBR,
		'left-bumper': e.BTN_TL,
		'left-trigger': e.BTN_TL2,
		'right-bumper': e.BTN_TR,
		'right-trigger': e.BTN_TR2,
		'y-button': e.BTN_NORTH,
		'x-button': e.BTN_EAST,
		'a-button': e.BTN_SOUTH,
		'b-button': e.BTN_WEST,
	}
	dpad = {
		'up-button': e.ABS_HAT0Y,
		'right-button': e.ABS_HAT0X,
		'down-button': e.ABS_HAT0Y,
		'left-button': e.ABS_HAT0X,
	}
	axes = {
		'left-stick-X': e.ABS_X,
		'left-stick-Y': e.ABS_Y,
		'right-stick-X': e.ABS_RX,
		'right-stick-Y': e.ABS_RY,
	}

	def __init__(self, device, addr):
		super().__init__(device, addr)
		self.type = "Sony Computer Entertainment Wireless Controller"
		self._ui = UInput(
			events=self.capabilities,
			name=self.type,
			vendor=1356,
			product=1476,
			version=273,
			bustype=e.BUS_USB,
		)

	def send(self, key, value):
		if key in self.buttons:
			logger.debug(f'Sending button event::{e.keys[self.buttons[key]]}: {value}')
			self._ui.write(e.EV_KEY, self.buttons[key], value)
			self._ui.syn()
		elif key in self.dpad:
			if key in {'up-button', 'left-button'}:
				value = 0 if value else 127
			else:
				value = 255 if value else 127
			logger.debug(f'Sending axis event::{e.ABS[self.dpad[key]]}: {value}')
			self._ui.write(e.EV_ABS, self.dpad[key], value)
			self._ui.syn()
		elif key in self.axes:
			coord = round(127 * value) + 127
			logger.debug(f'Sending axis event::{e.ABS[self.axes[key]]}: {coord}')
			self._ui.write(e.EV_ABS, self.axes[key], coord)
			self._ui.syn()
