# -*- mode: python ; coding: utf-8 -*-
# macOS build spec — run: pyinstaller tax_form_app.spec
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
    [],
    exclude_binaries=True,
    name='Bruno',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon='icon.icns',
    target_arch=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='Bruno',
)

app = BUNDLE(
    coll,
    name='Bruno.app',
    icon='icon.icns',
    bundle_identifier='com.bruno.taxform',
    info_plist={
        'CFBundleDisplayName': 'Bruno',
        'CFBundleShortVersionString': '2.0.0',
        'NSHighResolutionCapable': True,
    },
)
