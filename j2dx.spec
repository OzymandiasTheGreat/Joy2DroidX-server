# -*- mode: python ; coding: utf-8 -*-

import os
import platform
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules


APP = 'j2dx'
DEBUG = os.getenv('BUILD_MODE') == 'development'


block_cipher = None
hidden_imports = [
	'engineio.async_drivers.eventlet',
	*collect_submodules('eventlet.hubs'),
	*collect_submodules('dns'),
]


a = Analysis(
	['src/j2dx.py'],
	# pathex=['/home/ozymandias/Projects/Joy2DroidX-server'],
	pathex=[Path.cwd()],
	binaries=[],
	datas=[],
	hiddenimports=hidden_imports,
	hookspath=[],
	runtime_hooks=[],
	excludes=[],
	win_no_prefer_redirects=False,
	win_private_assemblies=False,
	cipher=block_cipher,
	noarchive=False,
)
pyz = PYZ(
	a.pure,
	a.zipped_data,
	cipher=block_cipher,
)
if platform.system() == 'Linux':
	exe = EXE(
		pyz,
		a.scripts,
		[],
		exclude_binaries=True,
		name=APP,
		debug=DEBUG,
		bootloader_ignore_signals=False,
		strip=False,
		upx=True,
		console=True,
	)
	coll = COLLECT(
		exe,
		a.binaries,
		a.zipfiles,
		a.datas,
		strip=False,
		upx=True,
		upx_exclude=[],
		name=APP,
	)
else:
	exe = EXE(
		pyz,
		a.scripts,
		a.binaries,
		a.zipfiles,
		a.datas,
		[],
		name=APP,
		debug=DEBUG,
		bootloader_ignore_signals=False,
		strip=False,
		upx=True,
		upx_exclude=[],
		runtime_tmpdir=None,
		console=True,
	)
