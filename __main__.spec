# -*- mode: python -*-
'''Cross-platform (MacOSX and Windows 10) Spec file for pyinstaller.
Be sure to not use python 3.7 until pyinstaller supports it.'''
# cSpell Checker - Correct Words****************************************
# // cSpell:words pyinstaller, pyspy, posix, icns, getcwd, datas,
# // cSpell:words tkinter, noconsole
# **********************************************************************
import os

if os.name == "nt":
    ICON_FILE = os.path.join("assets", "pyspy.ico")
elif os.name == "posix":
    ICON_FILE = os.path.join("assets", "pyspy.png")

MAC_ICON = os.path.join("assets", "pyspy.icns")
ABOUT_ICON = os.path.join("assets", "pyspy_mid.png")

block_cipher = None

a = Analysis(
    ["__main__.py"],
    pathex=[os.getcwd()],
    binaries=[],
    datas=[
        (ICON_FILE, "."),
        (ABOUT_ICON, "."),
        ("VERSION", "."),
        ("LICENSE.txt", "."),
        ],
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
