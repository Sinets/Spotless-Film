"""PyInstaller runtime hook: bundled LaMa checkpoint for IOPaint."""
from __future__ import annotations

import os
import sys


def _install() -> None:
    if not getattr(sys, "frozen", False) or not hasattr(sys, "_MEIPASS"):
        return
    # IOPaint resolves LaMa weights via torch.hub.get_dir() →
    # {TORCH_HOME}/hub/checkpoints/big-lama.pt (see iopaint/helper.py).
    base = os.path.join(sys._MEIPASS, "torch_cache")
    ckpt = os.path.join(base, "hub", "checkpoints", "big-lama.pt")
    if os.path.isfile(ckpt):
        os.environ.setdefault("TORCH_HOME", base)


_install()
