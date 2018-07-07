# -*- mode: python -*-
'''Cross-platform (MacOSX and Windows 10) Spec file for pyinstaller.
Be sure to not use python 3.7 until pytinstaller supports it.'''
# **********************************************************************
import os

if os.name == "nt":
    ICON_FILE = os.path.join("assets", "pyspy.ico")
elif os.name == "posix":
    ICON_FILE = os.path.join("assets", "pyspy.png")

MAC_ICON = os.path.join("assets", "pyspy.icns")

block_cipher = None

a = Analysis(
    ["__main__.py"],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[(ICON_FILE, ""),("VERSION","")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=["Tkinter"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
    )

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
    )

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="PySpy",
    icon=ICON_FILE,
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    noconsole=True,
    onefile=True,
    windowed=True
    )

app = BUNDLE(
    exe,
    name="PySpy.app",
    icon=MAC_ICON,
    bundle_identifier=None
    )
