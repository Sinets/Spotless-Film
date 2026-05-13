"""PyInstaller runtime hook: fix OpenCV cv2 bootstrap under macOS .app bundles.

During bootstrap OpenCV pops ``sys.modules['cv2']`` and calls
``importlib.import_module('cv2')`` to load ``cv2.abi3.so``. Frozen importers may
resolve that second import back to ``cv2/__init__.py`` while ``sys.OpenCV_LOADER`` is
set, causing recursion. When the loader flag is set, prefer the extension on disk.
"""
from __future__ import annotations

import importlib.abc
import importlib.machinery
import importlib.util
import pathlib
import sys
from importlib.machinery import ModuleSpec
from typing import Optional, Sequence


class _Cv2NativeBootstrapFinder(importlib.abc.MetaPathFinder):
    """Resolve the inner ``import cv2`` during OpenCV's bootstrap to the binary."""

    _CANDIDATES: Sequence[str] = ("cv2.abi3.so", "cv2.so")

    @classmethod
    def _extension_path(cls) -> Optional[str]:
        bad_suffixes = (".zip", ".egg")
        for entry in sys.path:
            if not entry or entry.endswith(bad_suffixes):
                continue
            base = pathlib.Path(entry)
            for name in cls._CANDIDATES:
                for cand in (base / "cv2" / name, base / name):
                    try:
                        resolved = cand.resolve()
                    except OSError:
                        continue
                    if resolved.is_file():
                        return str(resolved)
        return None

    def find_spec(
        self,
        fullname: str,
        path: object,
        target: object = None,
    ) -> Optional[ModuleSpec]:
        if fullname != "cv2" or not getattr(sys, "OpenCV_LOADER", False):
            return None
        ext_path = self._extension_path()
        if ext_path is None:
            return None
        loader = importlib.machinery.ExtensionFileLoader("cv2", ext_path)
        return importlib.util.spec_from_loader(
            "cv2",
            loader,
            origin=ext_path,
            is_package=False,
        )


def _install() -> None:
    if not getattr(sys, "frozen", False):
        return
    sys.meta_path.insert(0, _Cv2NativeBootstrapFinder())


_install()
