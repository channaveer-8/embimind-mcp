
import json

from pathlib import Path
from . import config


TARGETS_FILE = config.BASE_DIR / "targets.json"


def update_target(
    board_name: str,
    debugger: str,
    interface: str,
    target: str,
    transport: str = "swd"
) -> dict:
    """Save LLM-discovered OpenOCD configuration paths."""

    targets = {}

    if TARGETS_FILE.exists():
        with TARGETS_FILE.open("r", encoding="utf-8") as file:
            targets = json.load(file)

    targets[board_name] = {
        "debugger": debugger,
        "interface": interface,
        "target": target,
        "transport": transport
    }

    TARGETS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with TARGETS_FILE.open("w", encoding="utf-8") as file:
        json.dump(targets, file, indent=4)

    return targets[board_name]


def verify_target(board_name: str) -> dict:
    """Verify configuration paths against bundled OpenOCD scripts."""

    if not TARGETS_FILE.exists():
        raise FileNotFoundError("targets.json not found")

    with TARGETS_FILE.open("r", encoding="utf-8") as file:
        targets = json.load(file)

    if board_name not in targets:
        raise KeyError(f"Board not registered: {board_name}")

    target = targets[board_name]
    scripts_dir = config.OPENOCD_SCRIPTS.resolve()

    verified_paths = {}

    for key in ("interface", "target"):
        relative_path = Path(target[key])

        if relative_path.is_absolute():
            raise ValueError(f"{key} path must be relative")

        full_path = (scripts_dir / relative_path).resolve()

        try:
            full_path.relative_to(scripts_dir)
        except ValueError:
            raise ValueError(f"Invalid {key} path: outside scripts directory")

        if not full_path.is_file() or full_path.suffix.lower() != ".cfg":
            raise FileNotFoundError(f"{key} configuration not found: {full_path}")

        verified_paths[key] = str(full_path)

    return {
        "board_name": board_name,
        "debugger": target["debugger"],
        "transport": target["transport"],
        "interface_path": verified_paths["interface"],
        "target_path": verified_paths["target"],
        "verified": True
    }
