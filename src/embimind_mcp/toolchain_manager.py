import subprocess

from dataclasses import dataclass
from pathlib import Path

from . import config


@dataclass
class ToolchainInfo:
    openocd_path: Path
    openocd_scripts_path: Path
    gdb_path: Path
    openocd_version: str
    gdb_version: str


def check_file(path: Path, name: str):
    if not path.is_file():
        raise FileNotFoundError(
            f"{name} not found: {path}"
        )


def check_directory(path: Path, name: str):
    if not path.is_dir():
        raise FileNotFoundError(
            f"{name} directory not found: {path}"
        )


def check_executable(path: Path, name: str):

    try:
        result = subprocess.run(
            [str(path), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"{name} failed: {result.stderr}"
            )

        # Prefer stdout, fallback to stderr
        return result.stdout.strip() or result.stderr.strip()

    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"{name} version check timed out"
        )


def validate_toolchain() -> ToolchainInfo:

    # Check executable and script locations
    check_file(config.OPENOCD_EXE, "OpenOCD")
    check_directory(config.OPENOCD_SCRIPTS, "OpenOCD scripts")
    check_file(config.GDB_EXE, "ARM GDB")

    # Verify executables can run and capture their version strings
    openocd_version = check_executable(
        config.OPENOCD_EXE,
        "OpenOCD"
    )

    gdb_version = check_executable(
        config.GDB_EXE,
        "ARM GDB"
    )

    return ToolchainInfo(
        openocd_path=config.OPENOCD_EXE,
        openocd_scripts_path=config.OPENOCD_SCRIPTS,
        gdb_path=config.GDB_EXE,
        openocd_version=openocd_version,
        gdb_version=gdb_version,
    )
