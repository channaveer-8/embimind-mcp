"""
Firmware linking and static-library helpers for EmbiMind.

Final firmware linking uses the GCC driver rather than calling ld directly.
This lets GCC supply the appropriate runtime and linker support.
"""

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

from .arm_toolchain import run_tool

PathLike = Union[str, Path]
MAX_OUTPUT_CHARS = 4000


def _existing_files(files: Sequence[PathLike], description: str) -> List[Path]:
    if not files:
        raise ValueError("At least one {} must be provided".format(description))

    result = []
    for item in files:
        path = Path(item).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError("{} not found: {}".format(description, path))
        result.append(path)
    return result


def _format_result(result: Dict[str, object], output_path: Path) -> Dict[str, object]:
    return {
        "success": bool(result.get("success")),
        "tool": result.get("tool"),
        "output": str(output_path),
        "returncode": result.get("returncode"),
        "stdout": str(result.get("stdout", "")).strip()[-MAX_OUTPUT_CHARS:],
        "stderr": str(result.get("stderr", "")).strip()[-MAX_OUTPUT_CHARS:],
    }


def link_elf(
    object_files: Sequence[PathLike],
    output: PathLike,
    linker_script: Optional[PathLike] = None,
    flags: Optional[Sequence[str]] = None,
    library_dirs: Optional[Sequence[PathLike]] = None,
    libraries: Optional[Sequence[str]] = None,
    map_file: Optional[PathLike] = None,
    gc_sections: bool = False,
    print_memory_usage: bool = False,
    timeout: int = 120,
) -> Dict[str, object]:
    """Link object files into an ELF firmware image using arm-none-eabi-gcc."""
    objects = _existing_files(object_files, "object file")
    output_path = Path(output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    arguments = [str(flag) for flag in (flags or [])]

    if linker_script is not None:
        script = Path(linker_script).expanduser().resolve()
        if not script.is_file():
            raise FileNotFoundError("Linker script not found: {}".format(script))
        arguments.extend(["-T", str(script)])

    for directory in library_dirs or []:
        path = Path(directory).expanduser().resolve()
        if not path.is_dir():
            raise NotADirectoryError("Library directory not found: {}".format(path))
        arguments.extend(["-L", str(path)])

    arguments.extend(str(path) for path in objects)

    for library in libraries or []:
        name = str(library).strip()
        if not name:
            raise ValueError("Library names cannot be empty")
        arguments.append("-l" + name)

    if gc_sections:
        arguments.append("-Wl,--gc-sections")
    if print_memory_usage:
        arguments.append("-Wl,--print-memory-usage")

    if map_file is not None:
        map_path = Path(map_file).expanduser().resolve()
        map_path.parent.mkdir(parents=True, exist_ok=True)
        arguments.append("-Wl,-Map={}".format(map_path))

    arguments.extend(["-o", str(output_path)])

    result = run_tool(
        tool_name="gcc",
        arguments=arguments,
        cwd=output_path.parent,
        timeout=timeout,
    )
    return _format_result(result, output_path)


def create_static_library(
    object_files: Sequence[PathLike],
    output: PathLike,
    flags: str = "rcs",
    timeout: int = 60,
) -> Dict[str, object]:
    """Create a static archive (.a) from object files using arm-none-eabi-ar."""
    objects = _existing_files(object_files, "object file")
    output_path = Path(output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = run_tool(
        tool_name="ar",
        arguments=[flags, str(output_path)] + [str(path) for path in objects],
        cwd=output_path.parent,
        timeout=timeout,
    )
    return _format_result(result, output_path)


def index_static_library(
    archive: PathLike,
    timeout: int = 30,
) -> Dict[str, object]:
    """Generate or update the symbol index of an existing static archive."""
    archive_path = Path(archive).expanduser().resolve()
    if not archive_path.is_file():
        raise FileNotFoundError("Static library not found: {}".format(archive_path))

    result = run_tool(
        tool_name="ranlib",
        arguments=[str(archive_path)],
        cwd=archive_path.parent,
        timeout=timeout,
    )
    return _format_result(result, archive_path)
