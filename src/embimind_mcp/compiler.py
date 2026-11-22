"""
Firmware source compilation for EmbiMind.

Small wrappers around the ARM GNU compiler:
- compile C and C++ source files
- compile assembly source files
- preprocess source files

Flags are supplied by the caller. Board-specific defaults can be added later
when EmbiMind has a selected MCU configuration.
"""

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

from .arm_toolchain import run_tool

PathLike = Union[str, Path]
MAX_OUTPUT_CHARS = 4000


def _check_source(source: PathLike) -> Path:
    path = Path(source).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError("Source file not found: {}".format(path))
    return path


def _format_result(result: Dict[str, object], output_path: Path) -> Dict[str, object]:
    stdout = str(result.get("stdout", "")).strip()
    stderr = str(result.get("stderr", "")).strip()
    return {
        "success": bool(result.get("success")),
        "tool": result.get("tool"),
        "output": str(output_path),
        "returncode": result.get("returncode"),
        "stdout": stdout[-MAX_OUTPUT_CHARS:],
        "stderr": stderr[-MAX_OUTPUT_CHARS:],
    }


def _compile(
    tool: str,
    source: PathLike,
    output: Optional[PathLike] = None,
    flags: Optional[Sequence[str]] = None,
    include_dirs: Optional[Sequence[PathLike]] = None,
    defines: Optional[Sequence[str]] = None,
    timeout: int = 60,
) -> Dict[str, object]:
    source_path = _check_source(source)
    output_path = (
        Path(output).expanduser().resolve()
        if output is not None
        else source_path.with_suffix(".o")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    arguments: List[str] = [str(flag) for flag in (flags or [])]

    for directory in include_dirs or []:
        arguments.extend(["-I", str(Path(directory).expanduser().resolve())])

    for define in defines or []:
        arguments.extend(["-D", str(define)])

    arguments.extend(["-c", str(source_path), "-o", str(output_path)])

    result = run_tool(
        tool_name=tool,
        arguments=arguments,
        cwd=source_path.parent,
        timeout=timeout,
    )
    return _format_result(result, output_path)


def compile_c(
    source: PathLike,
    output: Optional[PathLike] = None,
    flags: Optional[Sequence[str]] = None,
    include_dirs: Optional[Sequence[PathLike]] = None,
    defines: Optional[Sequence[str]] = None,
    timeout: int = 60,
) -> Dict[str, object]:
    """Compile one C source file into an object file."""
    return _compile("gcc", source, output, flags, include_dirs, defines, timeout)


def compile_cpp(
    source: PathLike,
    output: Optional[PathLike] = None,
    flags: Optional[Sequence[str]] = None,
    include_dirs: Optional[Sequence[PathLike]] = None,
    defines: Optional[Sequence[str]] = None,
    timeout: int = 60,
) -> Dict[str, object]:
    """Compile one C++ source file into an object file."""
    return _compile("g++", source, output, flags, include_dirs, defines, timeout)


def compile_assembly(
    source: PathLike,
    output: Optional[PathLike] = None,
    flags: Optional[Sequence[str]] = None,
    timeout: int = 60,
) -> Dict[str, object]:
    """
    Compile .s or preprocessed .S assembly using the GCC driver.
    This keeps target options consistent with C and C++ compilation.
    """
    return _compile("gcc", source, output, flags, timeout=timeout)


def preprocess(
    source: PathLike,
    output: Optional[PathLike] = None,
    flags: Optional[Sequence[str]] = None,
    include_dirs: Optional[Sequence[PathLike]] = None,
    defines: Optional[Sequence[str]] = None,
    timeout: int = 60,
) -> Dict[str, object]:
    """Preprocess a C/C++ source file and write the result to .i by default."""
    source_path = _check_source(source)
    output_path = (
        Path(output).expanduser().resolve()
        if output is not None
        else source_path.with_suffix(".i")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    arguments: List[str] = [str(flag) for flag in (flags or [])]

    for directory in include_dirs or []:
        arguments.extend(["-I", str(Path(directory).expanduser().resolve())])

    for define in defines or []:
        arguments.extend(["-D", str(define)])

    arguments.extend(["-E", str(source_path), "-o", str(output_path)])

    result = run_tool(
        tool_name="gcc",
        arguments=arguments,
        cwd=source_path.parent,
        timeout=timeout,
    )
    return _format_result(result, output_path)
