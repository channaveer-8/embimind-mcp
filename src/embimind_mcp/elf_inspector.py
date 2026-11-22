"""
ELF inspection helpers for EmbiMind.

Provides concise wrappers around readelf, objdump, nm, size and addr2line.
The functions return captured output so the MCP layer can present only the
information needed by the user.
"""

from pathlib import Path
from typing import Dict, Optional, Sequence, Union

from .arm_toolchain import run_tool

PathLike = Union[str, Path]
MAX_OUTPUT_CHARS = 12000


def _check_file(path_value: PathLike) -> Path:
    path = Path(path_value).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError("File not found: {}".format(path))
    return path


def _run_inspector(
    tool: str,
    arguments: Sequence[str],
    input_file: PathLike,
    timeout: int = 30,
) -> Dict[str, object]:
    file_path = _check_file(input_file)
    args = [str(value) for value in arguments] + [str(file_path)]

    result = run_tool(
        tool_name=tool,
        arguments=args,
        cwd=file_path.parent,
        timeout=timeout,
    )

    return {
        "success": bool(result.get("success")),
        "tool": tool,
        "input": str(file_path),
        "returncode": result.get("returncode"),
        "output": str(result.get("stdout", "")).strip()[-MAX_OUTPUT_CHARS:],
        "stderr": str(result.get("stderr", "")).strip()[-4000:],
    }


def inspect_elf_header(elf_file: PathLike) -> Dict[str, object]:
    """Display ELF file header information."""
    return _run_inspector("readelf", ["-h"], elf_file)


def inspect_sections(elf_file: PathLike) -> Dict[str, object]:
    """Display ELF section headers."""
    return _run_inspector("readelf", ["-S"], elf_file)


def inspect_segments(elf_file: PathLike) -> Dict[str, object]:
    """Display ELF program headers/segments."""
    return _run_inspector("readelf", ["-l"], elf_file)


def inspect_symbols(
    elf_file: PathLike,
    demangle: bool = True,
    only_external: bool = False,
) -> Dict[str, object]:
    """List ELF symbols, optionally demangling C++ names."""
    flags = ["-C"] if demangle else []
    if only_external:
        flags.append("-g")
    return _run_inspector("nm", flags, elf_file)


def inspect_disassembly(
    elf_file: PathLike,
    source_interleaved: bool = False,
    all_sections: bool = False,
) -> Dict[str, object]:
    """Disassemble ELF code, optionally interleaving source lines."""
    flags = ["-D" if all_sections else "-d"]
    if source_interleaved:
        flags.append("-S")
    return _run_inspector("objdump", flags, elf_file)


def inspect_memory_usage(elf_file: PathLike) -> Dict[str, object]:
    """Report ELF section sizes in a compact Berkeley-style format."""
    return _run_inspector("size", ["-B"], elf_file)


def inspect_all_headers(elf_file: PathLike) -> Dict[str, object]:
    """Display ELF headers, sections, symbols and architecture information."""
    return _run_inspector("readelf", ["-a"], elf_file)


def address_to_source(
    elf_file: PathLike,
    addresses: Sequence[str],
    functions: bool = True,
    demangle: bool = True,
    timeout: int = 30,
) -> Dict[str, object]:
    """Translate one or more code addresses into source locations."""
    file_path = _check_file(elf_file)
    if not addresses:
        raise ValueError("Provide at least one address")

    arguments = ["-e", str(file_path)]
    if functions:
        arguments.append("-f")
    if demangle:
        arguments.append("-C")
    arguments.extend(str(address) for address in addresses)

    result = run_tool(
        tool_name="addr2line",
        arguments=arguments,
        cwd=file_path.parent,
        timeout=timeout,
    )

    return {
        "success": bool(result.get("success")),
        "tool": "addr2line",
        "input": str(file_path),
        "addresses": list(addresses),
        "returncode": result.get("returncode"),
        "output": str(result.get("stdout", "")).strip()[-MAX_OUTPUT_CHARS:],
        "stderr": str(result.get("stderr", "")).strip()[-4000:],
    }


def inspect_file_format(input_file: PathLike) -> Dict[str, object]:
    """Display object-file format and architecture information."""
    return _run_inspector("objdump", ["-f"], input_file)
