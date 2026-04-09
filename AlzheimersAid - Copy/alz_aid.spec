# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
import os
import kivymd

block_cipher = None

# Using directory names instead of wildcards for better compatibility with empty folders
added_files = [
    ('alz_app.kv', '.'),
    ('kv', 'kv'),
    ('screens', 'screens'),
    ('assets', 'assets'),
    ('fonts', 'fonts'),
    ('data', 'data'),
    ('audio', 'audio'),
    ('faces', 'faces'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('alz_app.kv', '.'),
        ('kv', 'kv'),
        ('screens', 'screens'),
        ('assets', 'assets'),
        ('fonts', 'fonts'),
        ('data', 'data'),
        ('audio', 'audio'),
        ('faces', 'faces'),
    ],
    hiddenimports=[
        'sqlite3',
        'pyttsx3',
        'pythoncom',
        'requests',
        'kivy',
        'kivymd',
        'kivymd.icon_definitions',
        'kivymd.uix.button',
        'kivymd.uix.label',
        'kivy.core.window',
        'kivy.uix.label',
        'kivy.uix.button',
        'kivy.lang',
    ],
    hookspath=[kivymd.hooks_path],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AlzheimersAid',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AlzheimersAid',
)

