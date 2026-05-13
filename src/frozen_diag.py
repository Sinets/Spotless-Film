"""Diagnostics when running as PyInstaller `--onefile`/windowless .exe."""
from __future__ import annotations

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path


def startup_trace_append(message: str) -> None:
    if not getattr(sys, "frozen", False):
        return
    try:
        base = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
        log_dir = base / "SpotlessFilm"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "startup_trace.log"
        with log_file.open("a", encoding="utf-8") as fh:
            fh.write(f"[{datetime.now().isoformat()}] {message}\n")
    except Exception:
        pass


def startup_report_fatal(exc: BaseException) -> None:
    """Last resort: persist traceback and show a Win32 alert for console-less binaries."""
    text = "".join(traceback.format_exception(exc))
    if not getattr(sys, "frozen", False):
        traceback.print_exc()
        return

    base = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
    log_dir = base / "SpotlessFilm"

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        err_log = log_dir / "startup_error.log"
        err_log.write_text(text, encoding="utf-8")
    except Exception:
        pass

    if sys.platform != "win32":
        traceback.print_exc()
        return

    try:
        import ctypes

        err_log = log_dir / "startup_error.log"
        ctypes.windll.user32.MessageBoxW(
            0,
            (
                "Spotless Film 启动失败。\n\n"
                f"错误详情已尝试写入：\n{err_log}\n\n"
                "若没有该文件，请在同目录查看 startup_trace.log。"
            ),
            "Spotless Film",
            0x10,
        )
    except Exception:
        traceback.print_exc()
