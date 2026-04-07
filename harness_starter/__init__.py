from __future__ import annotations

from pathlib import Path
import pkgutil


__path__ = pkgutil.extend_path(__path__, __name__)

SRC_PACKAGE_PATH = Path(__file__).resolve().parent.parent / "src" / "harness_starter"
if SRC_PACKAGE_PATH.is_dir():
    __path__.append(str(SRC_PACKAGE_PATH))
