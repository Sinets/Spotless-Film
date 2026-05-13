#!/usr/bin/env python3
"""PyInstaller entry: wraps imports so crashes are logged instead of disappearing."""
import multiprocessing as mp
import sys

from frozen_diag import startup_report_fatal, startup_trace_append


def _run() -> None:
    startup_trace_append("launcher: multiprocessing.freeze_support done")
    startup_trace_append("launcher: importing spotless_film_modern …")
    import spotless_film_modern as app

    startup_trace_append("launcher: calling spotless_film_modern.main() …")
    app.main()
    startup_trace_append("launcher: main() finished normally")


if __name__ == "__main__":
    mp.freeze_support()
    startup_trace_append("launcher: __main__, frozen=" + str(getattr(sys, "frozen", False)))
    try:
        _run()
    except BaseException as exc:
        startup_report_fatal(exc)
        startup_trace_append(f"launcher: fatal {type(exc).__name__}: {exc}")
        sys.exit(1)
