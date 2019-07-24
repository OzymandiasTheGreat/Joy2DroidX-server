import sys
from enum import IntFlag, IntEnum
from ctypes import Structure, WinDLL
from ctypes import c_ushort, c_short, c_byte, c_void_p, c_uint
from pkg_resources import resource_filename


if sys.maxsize > 2**32:
	ARCH = 'x64'
else:
	ARCH = 'x86'


XUSB_TRIGGER_MAX = 255
XUSB_THUMB_MAX = 32767


class VIGEM_TARGET_TYPE(IntFlag):
	Xbox360Wired    = 0
	XboxOneWired    = 1
	DualShock4Wired = 2


class XUSB_BUTTON(IntFlag):
	XUSB_GAMEPAD_DPAD_UP        = 0x0001
	XUSB_GAMEPAD_DPAD_DOWN      = 0x0002
	XUSB_GAMEPAD_DPAD_LEFT      = 0x0004
	XUSB_GAMEPAD_DPAD_RIGHT     = 0x0008
	XUSB_GAMEPAD_START          = 0x0010
	XUSB_GAMEPAD_BACK           = 0x0020
	XUSB_GAMEPAD_LEFT_THUMB     = 0x0040
	XUSB_GAMEPAD_RIGHT_THUMB    = 0x0080
	XUSB_GAMEPAD_LEFT_SHOULDER  = 0x0100
	XUSB_GAMEPAD_RIGHT_SHOULDER = 0x0200
	XUSB_GAMEPAD_GUIDE          = 0x0400
	XUSB_GAMEPAD_A              = 0x1000
	XUSB_GAMEPAD_B              = 0x2000
	XUSB_GAMEPAD_X              = 0x4000
	XUSB_GAMEPAD_Y              = 0x8000


class DS4_BUTTONS(IntFlag):
	DS4_BUTTON_THUMB_RIGHT      = 1 << 15
	DS4_BUTTON_THUMB_LEFT       = 1 << 14
	DS4_BUTTON_OPTIONS          = 1 << 13
	DS4_BUTTON_SHARE            = 1 << 12
	DS4_BUTTON_TRIGGER_RIGHT    = 1 << 11
	DS4_BUTTON_TRIGGER_LEFT     = 1 << 10
	DS4_BUTTON_SHOULDER_RIGHT   = 1 << 9
	DS4_BUTTON_SHOULDER_LEFT    = 1 << 8
	DS4_BUTTON_TRIANGLE         = 1 << 7
	DS4_BUTTON_CIRCLE           = 1 << 6
	DS4_BUTTON_CROSS            = 1 << 5
	DS4_BUTTON_SQUARE           = 1 << 4


class DS4_SPECIAL_BUTTONS(IntFlag):
	DS4_SPECIAL_BUTTON_PS       = 1 << 0
	DS4_SPECIAL_BUTTON_TOUCHPAD = 1 << 1


class DS4_DPAD_DIRECTIONS(IntEnum):
	DS4_BUTTON_DPAD_NONE        = 0x8
	DS4_BUTTON_DPAD_NORTHWEST   = 0x7
	DS4_BUTTON_DPAD_WEST        = 0x6
	DS4_BUTTON_DPAD_SOUTHWEST   = 0x5
	DS4_BUTTON_DPAD_SOUTH       = 0x4
	DS4_BUTTON_DPAD_SOUTHEAST   = 0x3
	DS4_BUTTON_DPAD_EAST        = 0x2
	DS4_BUTTON_DPAD_NORTHEAST   = 0x1
	DS4_BUTTON_DPAD_NORTH       = 0x0


class XUSB_REPORT(Structure):
	_fields_ = (
		('wButtons', c_ushort),
		('bLeftTrigger', c_byte),
		('bRightTrigger', c_byte),
		('sThumbLX', c_short),
		('sThumbLY', c_short),
		('sThumbRX', c_short),
		('sThumbRY', c_short),
	)


class DS4_REPORT(Structure):
	_fields_ = (
		('bThumbLX', c_byte),
		('bThumbLY', c_byte),
		('bThumbRX', c_byte),
		('bThumbRY', c_byte),
		('wButtons', c_ushort),
		('bSpecial', c_byte),
		('bTriggerL', c_byte),
		('bTriggerR', c_byte),
	)


def DS4_SET_DPAD(report, direction):
	report.wButtons &= ~0xF
	report.wButtons |= direction


def DS4_REPORT_INIT(report):
	report.bThumbLX = 0x80
	report.bThumbLY = 0x80
	report.bThumbRX = 0x80
	report.bThumbRY = 0x80
	DS4_SET_DPAD(report, DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)


class VIGEM_ERRORS(IntEnum):
	VIGEM_ERROR_NONE                        = 0x20000000
	VIGEM_ERROR_BUS_NOT_FOUND               = 0xE0000001
	VIGEM_ERROR_NO_FREE_SLOT                = 0xE0000002
	VIGEM_ERROR_INVALID_TARGET              = 0xE0000003
	VIGEM_ERROR_REMOVAL_FAILED              = 0xE0000004
	VIGEM_ERROR_ALREADY_CONNECTED           = 0xE0000005
	VIGEM_ERROR_TARGET_UNINITIALIZED        = 0xE0000006
	VIGEM_ERROR_TARGET_NOT_PLUGGED_IN       = 0xE0000007
	VIGEM_ERROR_BUS_VERSION_MISMATCH        = 0xE0000008
	VIGEM_ERROR_BUS_ACCESS_FAILED           = 0xE0000009
	VIGEM_ERROR_CALLBACK_ALREADY_REGISTERED = 0xE0000010
	VIGEM_ERROR_CALLBACK_NOT_FOUND          = 0xE0000011
	VIGEM_ERROR_BUS_ALREADY_CONNECTED       = 0xE0000012
	VIGEM_ERROR_BUS_INVALID_HANDLE          = 0xE0000013
	VIGEM_ERROR_XUSB_USERINDEX_OUT_OF_RANGE = 0xE0000014


if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
	# if ARCH == 'x64':
	# 	CLIENT = WinDLL('x64/ViGEmClient.dll')
	# else:
	# 	CLIENT = WinDLL('x86/ViGEmClient.dll')
	CLIENT = WinDLL(f'{ARCH}/ViGEmClient.dll')
else:
	CLIENT = WinDLL(resource_filename(f'{__package__}.{ARCH}', 'ViGEmClient.dll'))


alloc = CLIENT.vigem_alloc
alloc.argtypes = ()
alloc.restype = c_void_p


free = CLIENT.vigem_free
free.argtypes = (c_void_p,)
free.restype = None


connect = CLIENT.vigem_connect
connect.argtypes = (c_void_p,)
connect.restype = c_uint


disconnect = CLIENT.vigem_disconnect
disconnect.argtypes = (c_void_p,)
disconnect.restype = None


target_x360_alloc = CLIENT.vigem_target_x360_alloc
target_x360_alloc.argtypes = ()
target_x360_alloc.restype = c_void_p


target_ds4_alloc = CLIENT.vigem_target_ds4_alloc
target_ds4_alloc.argtypes = ()
target_ds4_alloc.restype = c_void_p


target_free = CLIENT.vigem_target_free
target_free.argtypes = (c_void_p,)
target_free.restype = None


target_add = CLIENT.vigem_target_add
target_add.argtypes = (c_void_p, c_void_p)
target_add.restype = c_uint


target_remove = CLIENT.vigem_target_remove
target_remove.argtypes = (c_void_p, c_void_p)
target_remove.restype = c_uint


target_x360_update = CLIENT.vigem_target_x360_update
target_x360_update.argtypes = (c_void_p, c_void_p, XUSB_REPORT)
target_x360_update.restype = c_uint


target_ds4_update = CLIENT.vigem_target_ds4_update
target_ds4_update.argtypes = (c_void_p, c_void_p, DS4_REPORT)
target_ds4_update.restype = c_uint
