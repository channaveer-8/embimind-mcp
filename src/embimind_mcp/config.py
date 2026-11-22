# -*- coding: utf-8 -*-
"""embimind_mcp configuration.

This module resolves paths to the bundled ARM GNU toolchain and OpenOCD
executables. When the package is installed from a wheel, the binaries live
inside the package under ``embimind_mcp/binaries``.  When running from a
source checkout we fall back to the traditional ``toolchain`` directory.
"""

from __future__ import annotations

import os
from pathlib import Path
import importlib.resources as resources

# ---------------------------------------------------------------------------
# Helper to locate a file that is packaged inside the wheel.
# ---------------------------------------------------------------------------
def _resource_path(*parts: str) -> Path:
    """Return an absolute :class:`Path` to a resource inside the package.

    ``importlib.resources`` works for both regular folders (editable install)
    and zip‑based wheels, so the same code works in every environment.
    """
    return Path(resources.files("embimind_mcp").joinpath(*parts))

# ---------------------------------------------------------------------------
# Base directory – used only when we are running from a source checkout.
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Primary locations (prefer bundled resources, fallback to source layout).
# ---------------------------------------------------------------------------
# The bundled toolchain lives under ``embimind_mcp/binaries/toolchain``.
_BUNDLED_TOOLCHAIN = _resource_path("binaries", "toolchain")

# Fallback paths (source tree) – keep the old behaviour for developers.
_SRC_TOOLCHAIN = BASE_DIR / "toolchain"

# Resolve the actual directory we will use.
if _BUNDLED_TOOLCHAIN.is_dir():
    TOOLCHAIN_DIR = _BUNDLED_TOOLCHAIN
else:
    TOOLCHAIN_DIR = _SRC_TOOLCHAIN

# ---------------------------------------------------------------------------
# Executable locations – handle the Windows ``.exe`` suffix automatically.
# ---------------------------------------------------------------------------
def _exe(name: str) -> Path:
    """Return the full path to an executable inside the toolchain.

    On Windows the files are ``*.exe``; on POSIX platforms the suffix is
    empty. ``os.name == "nt"`` is used to decide which suffix to apply.
    """
    suffix = ".exe" if os.name == "nt" else ""
    return TOOLCHAIN_DIR / "arm-gnu-toolchain" / "bin" / f"{name}{suffix}"

GDB_EXE = _exe("arm-none-eabi-gdb")
OPENOCD_EXE = _exe("openocd")  # OpenOCD lives directly under toolchain/openocd

# ---------------------------------------------------------------------------
# Backward‑compatible aliases (used by other modules).
# ---------------------------------------------------------------------------
# Some modules still import ``TOOLCHAIN_DIR`` from here; keep the name.
# ``OPENOCD_DIR`` and ``OPENOCD_EXE`` are also exported for compatibility.
OPENOCD_DIR = TOOLCHAIN_DIR / "openocd"

# ---------------------------------------------------------------------------
# End of configuration
# ---------------------------------------------------------------------------
