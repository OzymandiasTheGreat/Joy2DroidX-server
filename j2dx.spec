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

linux_data = [
	(f'assets/tk.ozymandias.{APP}.desktop', 'usr/share/applications'),
	(f'assets/tk.ozymandias.{APP}.svg', 'usr/share/icons/hicolor'),
	(f'assets/tk.ozymandias.{APP}.appdata.xml', 'usr/share/metainfo'),
]


if platform.system() == 'Linux':
	a = Analysis(
		['src/j2dx.py'],
		# pathex=['/home/ozymandias/Projects/Joy2DroidX-server'],
		pathex=[Path.cwd()],
		binaries=[],
		datas=linux_data,
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
	try:
		launcher = Path(f'{DISTPATH}/{APP}/tk.ozymandias.{APP}.desktop')
		if launcher.exists():
			launcher.unlink()
		launcher.symlink_to(f'usr/share/applications/tk.ozymandias.{APP}.desktop')
		icon = Path(f'{DISTPATH}/{APP}/tk.ozymandias.{APP}.svg')
		if icon.exists():
			icon.unlink()
		icon.symlink_to(f'usr/share/icons/hicolor/tk.ozymandias.{APP}.svg')
		dir_icon = Path(f'{DISTPATH}/{APP}/.DirIcon')
		if dir_icon.exists():
			dir_icon.unlink()
		dir_icon.symlink_to(f'usr/share/icons/hicolor/tk.ozymandias.{APP}.svg')
		app_run = Path(f'{DISTPATH}/{APP}/AppRun')
		if app_run.exists():
			app_run.unlink()
		app_run.symlink_to(f'{APP}')
	except Exception as e:
		print(f'ERROR CREATING SYMLINKS::{e.errno}')
else:
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
