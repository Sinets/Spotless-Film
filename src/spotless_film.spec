# -*- mode: python ; coding: utf-8 -*-
# PyInstaller injects Analysis, PYZ, EXE, BUNDLE, COLLECT when running this file.
# Also: SPECPATH (spec directory), SPEC — __file__ is NOT set when the spec is exec'd.
import os
import sys
from pathlib import Path

# Directory containing this .spec (portable; works in CI where __file__ is undefined)
_SPEC_ROOT = os.path.abspath(SPECPATH or os.getcwd())

block_cipher = None

datas: list[tuple[str, str]] = []
binaries: list[tuple[str, str, str]] = []

# Optional model weights shipped next to the project
_weights = Path(_SPEC_ROOT) / "weights"
if _weights.is_dir():
    for _w in sorted(_weights.glob("*.pth")):
        datas.append((str(_w), "weights"))

# CustomTkinter: bundle as explicit (src, dest_dir) tuples. A raw Tree() object
# cannot be placed in Analysis.datas — it raises ValueError unpacking tuples.
try:
    from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

    import customtkinter

    _ct_root = Path(customtkinter.__file__).resolve().parent
    for _p in sorted(_ct_root.rglob("*")):
        if not _p.is_file() or "__pycache__" in _p.parts:
            continue
        _rel = _p.relative_to(_ct_root)
        _dest_parent = Path("customtkinter") / _rel.parent
        datas.append((str(_p), str(_dest_parent).replace("\\", "/")))
    extra_hiddenimports = list(collect_submodules("customtkinter"))
except Exception as e:
    raise RuntimeError(
        "Install customtkinter before building (pip install customtkinter). "
        f"PyInstaller could not bundle it: {e}"
    ) from e

try:
    for _tpl in collect_dynamic_libs("tkinterdnd2"):
        binaries.append(_tpl)
except Exception:
    pass

# Entry script: launcher imports the real app inside try-exec so frozen builds
# log import/setup failures instead of exiting with no UI (Windows onefile exe).
a = Analysis(
    ["spotless_film_launcher.py"],
    pathex=[_SPEC_ROOT],
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
    icon=(
        str(Path(_SPEC_ROOT) / "icon.ico")
        if sys.platform == "win32" and (Path(_SPEC_ROOT) / "icon.ico").is_file()
        else None
    ),
)

# macOS .app bundle only — BUNDLE is not supported on Windows/Linux
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="SpotlessFilm.app",
        icon=(
            str(Path(_SPEC_ROOT) / "icon.icns")
            if (Path(_SPEC_ROOT) / "icon.icns").is_file()
            else None
        ),
        bundle_identifier="com.spotlessfilm.app",
        info_plist={
            "NSHighResolutionCapable": "True",
            "NSRequiresAquaSystemAppearance": "False",
        },
    )
