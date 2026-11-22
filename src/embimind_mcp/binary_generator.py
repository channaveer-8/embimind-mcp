"""
Firmware binary generation for EmbiMind.

Converts a linked ELF file into raw BIN or Intel HEX using objcopy.
The caller may provide additional objcopy options when needed.
"""

from pathlib import Path
from typing import Dict, Optional, Sequence, Union

from .arm_toolchain import run_tool

PathLike = Union[str, Path]
MAX_OUTPUT_CHARS = 4000


def _check_elf(elf_file: PathLike) -> Path:
    path = Path(elf_file).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError("ELF file not found: {}".format(path))
    return path


def _run_objcopy(
    elf_file: PathLike,
    output_file: PathLike,
    output_format: str,
    flags: Optional[Sequence[str]] = None,
    timeout: int = 60,
) -> Dict[str, object]:
    elf_path = _check_elf(elf_file)
    output_path = Path(output_file).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    arguments = [str(flag) for flag in (flags or [])]
    arguments.extend(["-O", output_format, str(elf_path), str(output_path)])

    result = run_tool(
        tool_name="objcopy",
        arguments=arguments,
        cwd=output_path.parent,
        timeout=timeout,
    )

    return {
        "success": bool(result.get("success")),
        "tool": result.get("tool"),
        "input": str(elf_path),
        "output": str(output_path),
        "format": output_format,
        "returncode": result.get("returncode"),
        "stdout": str(result.get("stdout", "")).strip()[-MAX_OUTPUT_CHARS:],
        "stderr": str(result.get("stderr", "")).strip()[-MAX_OUTPUT_CHARS:],
    }


def elf_to_bin(
    elf_file: PathLike,
    output_file: Optional[PathLike] = None,
    flags: Optional[Sequence[str]] = None,
    timeout: int = 60,
) -> Dict[str, object]:
    """Convert an ELF firmware image into a raw .bin file."""
    elf_path = _check_elf(elf_file)
    output_path = (
        Path(output_file).expanduser().resolve()
        if output_file is not None
        else elf_path.with_suffix(".bin")
    )
    return _run_objcopy(elf_path, output_path, "binary", flags, timeout)


def elf_to_hex(
    elf_file: PathLike,
    output_file: Optional[PathLike] = None,
    flags: Optional[Sequence[str]] = None,
    timeout: int = 60,
) -> Dict[str, object]:
    """Convert an ELF firmware image into an Intel HEX file."""
    elf_path = _check_elf(elf_file)
    output_path = (
        Path(output_file).expanduser().resolve()
        if output_file is not None
        else elf_path.with_suffix(".hex")
    )
    return _run_objcopy(elf_path, output_path, "ihex", flags, timeout)


def convert_elf(
    elf_file: PathLike,
    output_file: PathLike,
    output_format: str,
    flags: Optional[Sequence[str]] = None,
    timeout: int = 60,
) -> Dict[str, object]:
    """
    Convert ELF to another objcopy-supported format.

    Common output formats include: binary, ihex, srec, elf.
    The installed objcopy determines which formats are supported.
    """
    supported_formats = {"binary", "ihex", "srec", "elf"}
    normalized_format = output_format.strip().lower()

    if normalized_format not in supported_formats:
        raise ValueError(
            "Unsupported output format {!r}. Supported formats: {}".format(
                output_format, ", ".join(sorted(supported_formats))
            )
        )

    return _run_objcopy(
        elf_file,
        output_file,
        normalized_format,
        flags,
        timeout,
    )


def remove_elf_sections(
    elf_file: PathLike,
    output_file: PathLike,
    sections: Sequence[str],
    timeout: int = 60,
) -> Dict[str, object]:
    """Create a copy of an ELF file with the selected sections removed."""
    if not sections:
        raise ValueError("Provide at least one section name to remove")

    elf_path = _check_elf(elf_file)
    output_path = Path(output_file).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    arguments = []
    for section in sections:
        name = str(section).strip()
        if not name:
            raise ValueError("Section names cannot be empty")
        arguments.extend(["-R", name])

    arguments.extend([str(elf_path), str(output_path)])

    result = run_tool(
        tool_name="objcopy",
        arguments=arguments,
        cwd=output_path.parent,
        timeout=timeout,
    )

    return {
        "success": bool(result.get("success")),
        "tool": result.get("tool"),
        "input": str(elf_path),
        "output": str(output_path),
        "removed_sections": list(sections),
        "returncode": result.get("returncode"),
        "stdout": str(result.get("stdout", "")).strip()[-MAX_OUTPUT_CHARS:],
        "stderr": str(result.get("stderr", "")).strip()[-MAX_OUTPUT_CHARS:],
    }
