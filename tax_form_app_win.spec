# -*- mode: python ; coding: utf-8 -*-
# Windows build spec — run: pyinstaller tax_form_app_win.spec
import os

block_cipher = None
ROOT = os.path.abspath('.')

a = Analysis(
    ['src/tax_form_agent/gui.py'],
    pathex=[os.path.join(ROOT, 'src')],
    binaries=[],
    datas=[
        ('data/COMPLETE_FORM_STRUCTURE.json', 'data'),
        ('config.example.json', '.'),
        ('fonts', 'fonts'),
        ('icon.ico', '.'),
        ('icon.png', '.'),
    ],
    hiddenimports=['tax_form_agent'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'customtkinter'],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Bruno',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    version='version_win.txt' if os.path.exists('version_win.txt') else None,
    target_arch=None,
    runtime_tmpdir=None,
)
