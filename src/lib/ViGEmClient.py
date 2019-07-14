import sys
from enum import IntFlag, IntEnum
from ctypes import Structure, WinDLL
from ctypes import c_ushort, c_short, c_byte, c_void_p, c_uint


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


CLIENT = WinDLL(f'lib/{ARCH}/ViGEmClient.dll')


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
