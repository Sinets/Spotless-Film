#!/usr/bin/env python3
"""Download IOPaint LaMa JIT weights into src/bundle_models for PyInstaller."""
from __future__ import annotations

import hashlib
import sys
import urllib.error
import urllib.request
from pathlib import Path

LAMA_MODEL_URL = "https://github.com/Sanster/models/releases/download/add_big_lama/big-lama.pt"
LAMA_MODEL_MD5 = "e3aa4aaa15225a33ec84f9f4bc47e500"
_USER_AGENT = "SpotlessFilm-fetch-lama/1.0"

_SRC_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_DEST = (
    _SRC_ROOT / "bundle_models" / "torch_cache" / "hub" / "checkpoints" / "big-lama.pt"
)


def _md5_file(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _download_fixed_url(url: str, out_path: Path, timeout_sec: float = 600.0) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    # Fixed vendor URL above; timeouts bound hung CI builds.
    with urllib.request.urlopen(request, timeout=timeout_sec) as response, out_path.open(
        "wb"
    ) as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)


def main() -> int:
    dest = _DEFAULT_DEST
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file():
        if _md5_file(dest) == LAMA_MODEL_MD5:
            print(f"OK: LaMa checkpoint already valid: {dest}")
            return 0
        print("Existing checkpoint has wrong checksum, replacing…", flush=True)
        dest.unlink()

    print(f"Downloading LaMa → {dest} …", flush=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    try:
        _download_fixed_url(LAMA_MODEL_URL, tmp)
        if _md5_file(tmp) != LAMA_MODEL_MD5:
            tmp.unlink(missing_ok=True)
            print("Downloaded file failed md5 verification.", file=sys.stderr)
            return 1
        tmp.replace(dest)
    except (urllib.error.URLError, OSError, ValueError) as e:
        tmp.unlink(missing_ok=True)
        print(f"Download failed: {e}", file=sys.stderr)
        return 1

    print(f"OK: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
