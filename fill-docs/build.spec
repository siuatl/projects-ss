# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

datas_pypdf, binaries_pypdf, hiddenimports_pypdf = collect_all("pypdf")
datas_openpyxl, binaries_openpyxl, hiddenimports_openpyxl = collect_all("openpyxl")

import gooey

gooey_root = os.path.dirname(gooey.__file__)

block_cipher = None

a = Analysis(
    ["fill-docs.py"],
    pathex=["./fill-docs.py"],
    binaries=binaries_pypdf + binaries_openpyxl,
    datas=datas_pypdf + datas_openpyxl,
    hiddenimports=["pypdf", "gooey"] + hiddenimports_openpyxl,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="fill-docs",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=os.path.join(gooey_root, "images", "program_icon.ico"),
)
