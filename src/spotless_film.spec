# -*- mode: python ; coding: utf-8 -*-
# PyInstaller injects Analysis, PYZ, EXE, BUNDLE, COLLECT when running this file.
import sys
from pathlib import Path

block_cipher = None

datas: list[tuple[str, str]] = []
binaries: list[tuple[str, str, str]] = []

# Optional model weights shipped next to the project
_weights = Path("weights")
if _weights.is_dir():
    for _w in sorted(_weights.glob("*.pth")):
        datas.append((str(_w), "weights"))

# CustomTkinter assets (themes, fonts) — required for packaged GUI on all OSes
try:
    from PyInstaller.utils.hooks import collect_all

    _ctd, _ctb, _ct_hidden = collect_all("customtkinter")
    datas += _ctd
    binaries += _ctb
    extra_hiddenimports = list(_ct_hidden)
except Exception:
    extra_hiddenimports = []

a = Analysis(
    ["spotless_film_modern.py"],
    pathex=[str(Path(__file__).resolve().parent)],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        "torch",
        "torchvision",
        "PIL",
        "PIL.Image",
        "PIL.ImageTk",
        "customtkinter",
        "tkinter",
        "tkinterdnd2",
        "numpy",
        "cv2",
        "threading",
        "dataclasses",
        "enum",
        "typing",
    ]
    + extra_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "jupyter",
        "notebook",
        "ipython",
        "pandas",
        "scipy",
        "sklearn",
        "tensorflow",
    ],
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
    name="SpotlessFilm",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="icon.ico" if sys.platform == "win32" and Path("icon.ico").is_file() else None,
)

# macOS .app bundle only — BUNDLE is not supported on Windows/Linux
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="SpotlessFilm.app",
        icon="icon.icns" if Path("icon.icns").is_file() else None,
        bundle_identifier="com.spotlessfilm.app",
        info_plist={
            "NSHighResolutionCapable": "True",
            "NSRequiresAquaSystemAppearance": "False",
        },
    )
