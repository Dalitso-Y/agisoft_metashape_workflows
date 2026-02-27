from __future__ import annotations
import os
import time
from typing import Optional

class Logger:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path

    def _write(self, level: str, msg: str) -> None:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {level}: {msg}"
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        # Also print to Metashape console / stdout
        try:
            print(line)
        except Exception:
            pass

    def info(self, msg: str) -> None:
        self._write("INFO", msg)

    def warn(self, msg: str) -> None:
        self._write("WARN", msg)

    def error(self, msg: str) -> None:
        self._write("ERROR", msg)