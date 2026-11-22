"""
ARM GNU Toolchain registry and execution layer for EmbiMind.

Responsibilities
----------------
1. Maintain a central registry of ARM GNU Toolchain executables.
2. Keep executable-specific option metadata together in that registry.
3. Discover installed executables in the bundled toolchain directory.
4. Report toolchain and executable versions.
5. Retrieve the installed executable's own help output.
6. Execute a registered tool safely without invoking a shell.

The option metadata is an EmbiMind reference, not a complete copy of each
program's manual. The installed executable's help output and actual exit status
remain the runtime authority for supported options.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from . import config


PathLike = Union[str, Path]


class ToolchainError(RuntimeError):
    """Raised when a toolchain executable is missing or cannot be run."""


# ---------------------------------------------------------------------------
# 1. Central executable and option registry
# ---------------------------------------------------------------------------
#
# Each tool owns its own option definitions here.
#
# Option metadata fields:
#   description : Human-readable explanation.
#   argument    : Whether the option expects a following value.
#   example     : Illustrative usage (optional).
#   note        : Important usage constraint (optional).
#
# This is intentionally a curated starting set of commonly used options.
# It is not intended to enumerate every option supported by GNU binutils/GCC.
# Use get_tool_help() to inspect the installed executable's full help output.

TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ------------------------- Compiler family -------------------------
    "gcc": {
        "executable": "arm-none-eabi-gcc.exe",
        "category": "compiler",
        "description": "GNU C compiler and driver; also drives the link step.",
        "options": {
            "target": {
                "-mcpu": {
                    "description": "Select the target processor.",
                    "argument": True,
                    "example": "-mcpu=cortex-m4",
                    "note": "The CPU name must be supported by this GCC build.",
                },
                "-march": {
                    "description": "Select the target architecture.",
                    "argument": True,
                },
                "-mthumb": {
                    "description": "Generate Thumb instructions.",
                    "argument": False,
                },
                "-mfpu": {
                    "description": "Select the floating-point unit instruction set.",
                    "argument": True,
                    "example": "-mfpu=fpv4-sp-d16",
                },
                "-mfloat-abi": {
                    "description": "Select the floating-point calling convention.",
                    "argument": True,
                    "example": "-mfloat-abi=hard",
                },
            },
            "optimization": {
                "-O0": {"description": "Disable most optimizations.", "argument": False},
                "-O1": {"description": "Enable basic optimization.", "argument": False},
                "-O2": {"description": "Optimize for performance.", "argument": False},
                "-O3": {"description": "Enable more aggressive optimizations.", "argument": False},
                "-Os": {"description": "Optimize for code size.", "argument": False},
                "-Og": {"description": "Optimize while preserving a useful debugging experience.", "argument": False},
            },
            "debug": {
                "-g": {"description": "Generate debugging information.", "argument": False},
                "-gdwarf": {"description": "Select the DWARF debug information format/version.", "argument": True},
            },
            "warnings": {
                "-Wall": {"description": "Enable a broad set of common warnings.", "argument": False},
                "-Wextra": {"description": "Enable additional warnings.", "argument": False},
                "-Werror": {"description": "Treat warnings as errors.", "argument": False},
                "-Wpedantic": {"description": "Request stricter ISO language diagnostics.", "argument": False},
            },
            "preprocessor": {
                "-I": {"description": "Add a header-file search directory.", "argument": True},
                "-isystem": {"description": "Add a system header search directory.", "argument": True},
                "-D": {"description": "Define a preprocessor macro.", "argument": True},
                "-U": {"description": "Undefine a preprocessor macro.", "argument": True},
                "-include": {"description": "Process a file before the main source file.", "argument": True},
            },
            "compilation": {
                "-c": {"description": "Compile or assemble without linking.", "argument": False},
                "-S": {"description": "Compile to assembly without assembling.", "argument": False},
                "-E": {"description": "Preprocess only.", "argument": False},
                "-o": {"description": "Set the output file.", "argument": True},
                "-std": {"description": "Select the C language standard.", "argument": True},
                "-x": {"description": "Specify the language of the following input.", "argument": True},
                "-M": {"description": "Generate make-style header dependencies.", "argument": False},
                "-MMD": {"description": "Generate user-header dependencies.", "argument": False},
                "-MP": {"description": "Add phony dependency targets.", "argument": False},
            },
            "code_generation": {
                "-ffunction-sections": {"description": "Place each function in its own section.", "argument": False},
                "-fdata-sections": {"description": "Place each data item in its own section.", "argument": False},
                "-fno-builtin": {"description": "Do not recognize built-in function names.", "argument": False},
                "-flto": {"description": "Enable link-time optimization.", "argument": False},
            },
            "link_driver": {
                "-T": {"description": "Use the specified linker script.", "argument": True},
                "-L": {"description": "Add a library search directory.", "argument": True},
                "-l": {"description": "Link a library.", "argument": True},
                "-Wl,": {"description": "Forward comma-separated options to the linker.", "argument": True},
                "-nostartfiles": {"description": "Do not use standard startup files.", "argument": False},
                "-nostdlib": {"description": "Do not use standard system startup files or libraries.", "argument": False},
                "-specs": {"description": "Use the specified GCC specs file.", "argument": True},
            },
        },
    },
    "g++": {
        "executable": "arm-none-eabi-g++.exe",
        "category": "compiler",
        "description": "GNU C++ compiler driver.",
        "options": {
            "language": {
                "-std": {"description": "Select the C++ language standard.", "argument": True},
                "-fno-exceptions": {"description": "Disable C++ exception handling.", "argument": False},
                "-fno-rtti": {"description": "Disable run-time type information.", "argument": False},
                "-fno-threadsafe-statics": {"description": "Disable thread-safe initialization of local statics.", "argument": False},
            },
            "common_driver": {
                "-mcpu": {"description": "Select the target processor.", "argument": True},
                "-mthumb": {"description": "Generate Thumb instructions.", "argument": False},
                "-O0": {"description": "Disable most optimizations.", "argument": False},
                "-O1": {"description": "Enable basic optimization.", "argument": False},
                "-O2": {"description": "Optimize for performance.", "argument": False},
                "-O3": {"description": "Enable more aggressive optimizations.", "argument": False},
                "-Os": {"description": "Optimize for code size.", "argument": False},
                "-g": {"description": "Generate debugging information.", "argument": False},
                "-Wall": {"description": "Enable common warnings.", "argument": False},
                "-Wextra": {"description": "Enable additional warnings.", "argument": False},
                "-I": {"description": "Add a header search directory.", "argument": True},
                "-D": {"description": "Define a preprocessor macro.", "argument": True},
                "-c": {"description": "Compile without linking.", "argument": False},
                "-o": {"description": "Set the output file.", "argument": True},
            },
        },
    },
    "cpp": {
        "executable": "arm-none-eabi-cpp.exe",
        "category": "preprocessor",
        "description": "GNU C/C++ preprocessor.",
        "options": {
            "include_paths": {
                "-I": {"description": "Add a header search directory.", "argument": True},
                "-iquote": {"description": "Add a quote-only include directory.", "argument": True},
                "-isystem": {"description": "Add a system include directory.", "argument": True},
                "-include": {"description": "Include a file before processing the input.", "argument": True},
            },
            "macros": {
                "-D": {"description": "Define a macro.", "argument": True},
                "-U": {"description": "Undefine a macro.", "argument": True},
            },
            "output": {
                "-o": {"description": "Set the preprocessor output file.", "argument": True},
                "-P": {"description": "Suppress line markers.", "argument": False},
                "-C": {"description": "Do not discard comments.", "argument": False},
            },
        },
    },
    "as": {
        "executable": "arm-none-eabi-as.exe",
        "category": "assembler",
        "description": "GNU assembler.",
        "options": {
            "input_output": {
                "-o": {"description": "Set the object output file.", "argument": True},
                "-I": {"description": "Add an include search directory.", "argument": True},
                "-al": {"description": "Generate an assembly listing.", "argument": False},
            },
            "target": {
                "-mcpu": {"description": "Select the target processor.", "argument": True},
                "-mthumb": {"description": "Assemble Thumb instructions where supported.", "argument": False},
                "-mfpu": {"description": "Select the floating-point unit.", "argument": True},
            },
        },
    },

    # --------------------------- Linker family -------------------------
    "ld": {
        "executable": "arm-none-eabi-ld.exe",
        "category": "linker",
        "description": "GNU linker.",
        "options": {
            "script_and_output": {
                "-T": {"description": "Use a linker script.", "argument": True},
                "-o": {"description": "Set the output file.", "argument": True},
                "-Map": {"description": "Write a linker map file.", "argument": True},
                "--gc-sections": {"description": "Discard unused input sections.", "argument": False},
                "--print-memory-usage": {"description": "Display memory region usage from the linker script.", "argument": False},
            },
            "search_and_libraries": {
                "-L": {"description": "Add a library search directory.", "argument": True},
                "-l": {"description": "Search for a library.", "argument": True},
                "--start-group": {"description": "Start a group of archives for repeated searching.", "argument": False},
                "--end-group": {"description": "End a group of archives.", "argument": False},
            },
            "symbols_and_layout": {
                "--defsym": {"description": "Define a linker symbol.", "argument": True},
                "--cref": {"description": "Generate a cross-reference table.", "argument": False},
                "--orphan-handling": {"description": "Control handling of orphan sections.", "argument": True},
            },
        },
    },
    "ld.bfd": {
        "executable": "arm-none-eabi-ld.bfd.exe",
        "category": "linker",
        "description": "GNU BFD linker backend.",
        "options": {
            "script_and_output": {
                "-T": {"description": "Use a linker script.", "argument": True},
                "-o": {"description": "Set the output file.", "argument": True},
                "-Map": {"description": "Write a linker map file.", "argument": True},
                "--gc-sections": {"description": "Discard unused input sections.", "argument": False},
                "--print-memory-usage": {"description": "Display memory region usage.", "argument": False},
            },
        },
    },
    "ar": {
        "executable": "arm-none-eabi-ar.exe",
        "category": "archive",
        "description": "Create, modify and inspect static archives.",
        "options": {
            "operations": {
                "r": {"description": "Insert or replace members.", "argument": False},
                "c": {"description": "Create the archive if needed without a creation warning.", "argument": False},
                "s": {"description": "Write an archive symbol index.", "argument": False},
                "t": {"description": "List archive members.", "argument": False},
                "x": {"description": "Extract archive members.", "argument": False},
                "d": {"description": "Delete archive members.", "argument": False},
                "q": {"description": "Quickly append members.", "argument": False},
                "v": {"description": "Enable verbose output.", "argument": False},
            },
        },
    },
    "ranlib": {
        "executable": "arm-none-eabi-ranlib.exe",
        "category": "archive",
        "description": "Generate or update an archive symbol index.",
        "options": {
            "general": {
                "-t": {"description": "Update the archive symbol map.", "argument": False},
                "-D": {"description": "Use deterministic archive mode where supported.", "argument": False},
                "-v": {"description": "Display the ranlib version.", "argument": False},
            },
        },
    },
    "gcc-ar": {
        "executable": "arm-none-eabi-gcc-ar.exe",
        "category": "archive",
        "description": "GCC wrapper around ar, supporting plugin/LTO integration.",
        "options": {
            "operations": {
                "r": {"description": "Insert or replace archive members.", "argument": False},
                "s": {"description": "Write an archive symbol index.", "argument": False},
                "t": {"description": "List archive members.", "argument": False},
                "x": {"description": "Extract archive members.", "argument": False},
            },
        },
    },
    "gcc-ranlib": {
        "executable": "arm-none-eabi-gcc-ranlib.exe",
        "category": "archive",
        "description": "GCC wrapper around ranlib, supporting plugin/LTO integration.",
        "options": {
            "general": {
                "-t": {"description": "Update the archive symbol map.", "argument": False},
            },
        },
    },

    # ----------------------- Binary and ELF utilities ------------------
    "objcopy": {
        "executable": "arm-none-eabi-objcopy.exe",
        "category": "binary_generator",
        "description": "Copy and translate object files and executable formats.",
        "options": {
            "format": {
                "-O": {"description": "Set the output object format.", "argument": True, "example": "-O binary"},
                "-I": {"description": "Set the input object format.", "argument": True},
                "-B": {"description": "Set the output architecture.", "argument": True},
            },
            "sections": {
                "-j": {"description": "Copy only the named section.", "argument": True},
                "-R": {"description": "Remove the named section.", "argument": True},
                "--only-section": {"description": "Copy only the named section.", "argument": True},
                "--remove-section": {"description": "Remove the named section.", "argument": True},
                "--set-section-flags": {"description": "Set flags for a section.", "argument": True},
            },
            "address_and_symbols": {
                "--change-addresses": {"description": "Adjust section VMA and LMA addresses.", "argument": True},
                "--adjust-vma": {"description": "Add an offset to section VMAs.", "argument": True},
                "--add-symbol": {"description": "Add a symbol to the output file.", "argument": True},
                "--strip-debug": {"description": "Remove debugging symbols and sections.", "argument": False},
                "--strip-all": {"description": "Remove all symbols.", "argument": False},
            },
        },
    },
    "strip": {
        "executable": "arm-none-eabi-strip.exe",
        "category": "binary_generator",
        "description": "Discard symbols and other information from object files.",
        "options": {
            "symbol_removal": {
                "-s": {"description": "Remove all symbols.", "argument": False},
                "-g": {"description": "Remove debugging symbols only.", "argument": False},
                "-S": {"description": "Remove debugging symbols and sections.", "argument": False},
                "-x": {"description": "Do not copy non-global symbols.", "argument": False},
                "-o": {"description": "Write output to a separate file.", "argument": True},
            },
        },
    },
    "objdump": {
        "executable": "arm-none-eabi-objdump.exe",
        "category": "elf_inspector",
        "description": "Display information about object files and disassemble code.",
        "options": {
            "disassembly": {
                "-d": {"description": "Disassemble executable sections.", "argument": False},
                "-D": {"description": "Disassemble all non-empty sections.", "argument": False},
                "-S": {"description": "Intermix source code with disassembly when available.", "argument": False},
                "-M": {"description": "Select disassembly options.", "argument": True},
            },
            "headers_and_sections": {
                "-f": {"description": "Display file headers.", "argument": False},
                "-h": {"description": "Display section headers.", "argument": False},
                "-p": {"description": "Display private headers.", "argument": False},
                "-x": {"description": "Display all available headers.", "argument": False},
                "-s": {"description": "Display full section contents.", "argument": False},
            },
            "symbols": {
                "-t": {"description": "Display the symbol table.", "argument": False},
                "-T": {"description": "Display dynamic symbols.", "argument": False},
                "-r": {"description": "Display relocation entries.", "argument": False},
            },
        },
    },
    "readelf": {
        "executable": "arm-none-eabi-readelf.exe",
        "category": "elf_inspector",
        "description": "Display information about ELF files.",
        "options": {
            "headers": {
                "-h": {"description": "Display the ELF file header.", "argument": False},
                "-l": {"description": "Display program headers.", "argument": False},
                "-S": {"description": "Display section headers.", "argument": False},
                "-e": {"description": "Display all headers.", "argument": False},
            },
            "symbols_and_relocations": {
                "-s": {"description": "Display the symbol table.", "argument": False},
                "-r": {"description": "Display relocation entries.", "argument": False},
                "-d": {"description": "Display dynamic section information.", "argument": False},
                "-A": {"description": "Display architecture-specific information.", "argument": False},
            },
            "debug": {
                "-w": {"description": "Display DWARF debug information.", "argument": False},
                "-a": {"description": "Display all information.", "argument": False},
            },
        },
    },
    "nm": {
        "executable": "arm-none-eabi-nm.exe",
        "category": "elf_inspector",
        "description": "List symbols from object files.",
        "options": {
            "symbol_selection": {
                "-a": {"description": "Display all symbols, including debug-only symbols.", "argument": False},
                "-g": {"description": "Display only external symbols.", "argument": False},
                "-u": {"description": "Display only undefined symbols.", "argument": False},
                "-C": {"description": "Demangle C++ symbol names.", "argument": False},
            },
            "sorting_and_format": {
                "-n": {"description": "Sort symbols by address.", "argument": False},
                "-S": {"description": "Display symbol sizes.", "argument": False},
                "-P": {"description": "Use portable output format.", "argument": False},
                "-A": {"description": "Print the filename before each symbol.", "argument": False},
            },
        },
    },
    "size": {
        "executable": "arm-none-eabi-size.exe",
        "category": "elf_inspector",
        "description": "Report section sizes and total memory footprint.",
        "options": {
            "format": {
                "-A": {"description": "Display section sizes in Berkeley format.", "argument": False},
                "-B": {"description": "Display sizes in Berkeley format.", "argument": False},
                "--format": {"description": "Select the output format.", "argument": True},
                "-x": {"description": "Display sizes in hexadecimal.", "argument": False},
                "-d": {"description": "Display sizes in decimal.", "argument": False},
            },
        },
    },
    "addr2line": {
        "executable": "arm-none-eabi-addr2line.exe",
        "category": "elf_inspector",
        "description": "Translate addresses into source file and line information.",
        "options": {
            "lookup": {
                "-e": {"description": "Specify the executable or object file.", "argument": True},
                "-f": {"description": "Display function names.", "argument": False},
                "-C": {"description": "Demangle C++ names.", "argument": False},
                "-i": {"description": "Display inline call information.", "argument": False},
                "-p": {"description": "Display output on one line.", "argument": False},
            },
        },
    },
    "strings": {
        "executable": "arm-none-eabi-strings.exe",
        "category": "elf_inspector",
        "description": "Print sequences of printable characters from files.",
        "options": {
            "selection": {
                "-a": {"description": "Scan the whole file.", "argument": False},
                "-n": {"description": "Set the minimum string length.", "argument": True},
                "-t": {"description": "Print the string offset using the selected radix.", "argument": True},
                "-e": {"description": "Select character encoding.", "argument": True},
            },
        },
    },
    "c++filt": {
        "executable": "arm-none-eabi-c++filt.exe",
        "category": "elf_inspector",
        "description": "Demangle encoded C++ symbol names.",
        "options": {
            "demangling": {
                "-n": {"description": "Do not demangle names that are already demangled.", "argument": False},
                "-p": {"description": "Do not display function parameters.", "argument": False},
                "-t": {"description": "Demangle types as well as function names.", "argument": False},
            },
        },
    },
    "elfedit": {
        "executable": "arm-none-eabi-elfedit.exe",
        "category": "elf_inspector",
        "description": "Update ELF file metadata.",
        "options": {
            "general": {
                "--input-mach": {"description": "Set or change the input machine type.", "argument": True},
                "--output-mach": {"description": "Set or change the output machine type.", "argument": True},
                "--input-type": {"description": "Set or change the input ELF type.", "argument": True},
                "--output-type": {"description": "Set or change the output ELF type.", "argument": True},
            },
        },
    },

    # ----------------------- Coverage / profiling ----------------------
    "gcov": {
        "executable": "arm-none-eabi-gcov.exe",
        "category": "coverage",
        "description": "Generate source coverage reports from GCC coverage data.",
        "options": {
            "reports": {
                "-a": {"description": "Write individual block counts.", "argument": False},
                "-b": {"description": "Write branch frequencies.", "argument": False},
                "-c": {"description": "Write branch counts rather than percentages.", "argument": False},
                "-f": {"description": "Display function summaries.", "argument": False},
                "-o": {"description": "Specify the object or data-file directory.", "argument": True},
            },
        },
    },
    "gcov-dump": {
        "executable": "arm-none-eabi-gcov-dump.exe",
        "category": "coverage",
        "description": "Dump information from GCC coverage data files.",
        "options": {
            "output": {
                "-l": {"description": "Display detailed record information.", "argument": False},
                "-p": {"description": "Display file names in absolute paths where supported.", "argument": False},
                "-v": {"description": "Display version information.", "argument": False},
            },
        },
    },
    "gcov-tool": {
        "executable": "arm-none-eabi-gcov-tool.exe",
        "category": "coverage",
        "description": "Process and merge GCC coverage data.",
        "options": {
            "operations": {
                "merge": {"description": "Merge profile data directories.", "argument": True},
                "rewrite": {"description": "Rewrite profile data.", "argument": True},
                "overlap": {"description": "Compare profile data.", "argument": True},
            },
        },
    },
    "gprof": {
        "executable": "arm-none-eabi-gprof.exe",
        "category": "profiling",
        "description": "Display profiling information from gprof data.",
        "options": {
            "reports": {
                "-b": {"description": "Suppress verbose explanations.", "argument": False},
                "-p": {"description": "Generate a flat profile.", "argument": False},
                "-q": {"description": "Generate a call graph.", "argument": False},
                "-A": {"description": "Annotate source files.", "argument": False},
            },
        },
    },
    "lto-dump": {
        "executable": "arm-none-eabi-lto-dump.exe",
        "category": "lto",
        "description": "Inspect GCC link-time optimization object information.",
        "options": {
            "general": {
                "-list": {"description": "List available LTO information.", "argument": False},
                "-demangle": {"description": "Demangle symbol names in output.", "argument": False},
            },
        },
    },

    # ----------------------------- Debugger ----------------------------
    "gdb": {
        "executable": "arm-none-eabi-gdb.exe",
        "category": "debugger",
        "description": "GNU debugger for ARM bare-metal targets.",
        "options": {
            "startup": {
                "-q": {"description": "Suppress introductory messages.", "argument": False},
                "-batch": {"description": "Run in batch mode and exit.", "argument": False},
                "-x": {"description": "Execute commands from a GDB command file.", "argument": True},
                "-ex": {"description": "Execute a GDB command.", "argument": True},
                "--symbols": {"description": "Load symbols from an executable file.", "argument": True},
                "--core": {"description": "Specify a core dump file.", "argument": True},
            },
        },
    },
    "gdb-py": {
        "executable": "arm-none-eabi-gdb-py.exe",
        "category": "debugger",
        "description": "Python-enabled GNU debugger, if included in this toolchain build.",
        "options": {
            "startup": {
                "-q": {"description": "Suppress introductory messages.", "argument": False},
                "-batch": {"description": "Run in batch mode and exit.", "argument": False},
                "-x": {"description": "Execute commands from a GDB command file.", "argument": True},
            },
        },
    },
}


# Executables used for a normal C/C++ bare-metal firmware workflow.
# Advanced tools are discovered and reported, but are not mandatory.
REQUIRED_TOOLS = (
    "gcc",
    "g++",
    "as",
    "ld",
    "ar",
    "objcopy",
    "objdump",
    "readelf",
    "nm",
    "size",
    "gdb",
)


@dataclass(frozen=True)
class ToolchainInfo:
    """Structured summary of the bundled ARM GNU Toolchain."""

    bin_dir: Path
    gcc_version: str
    available_tools: Dict[str, Path]
    missing_required_tools: List[str]
    unregistered_executables: List[str]

    @property
    def is_valid(self) -> bool:
        return not self.missing_required_tools


# ---------------------------------------------------------------------------
# 2. Paths and executable discovery
# ---------------------------------------------------------------------------

def get_toolchain_bin_dir() -> Path:
    """Return the bundled ARM GNU Toolchain bin directory."""
    return (
        Path(config.TOOLCHAIN_DIR) / "arm-gnu-toolchain" / "bin"
    ).resolve()


def get_executable(
    tool_name: str,
    bin_dir: Optional[PathLike] = None,
) -> Path:
    """
    Resolve a registered tool name to its executable.

    Pass registry keys such as 'gcc', 'objcopy', 'readelf' or 'gdb'.
    Arbitrary executable paths and unregistered names are rejected.
    """
    name = tool_name.strip().lower()

    if name not in TOOL_REGISTRY:
        raise ToolchainError(
            "Unknown registered tool {!r}. Use get_registered_tools() "
            "to list supported names.".format(tool_name)
        )

    directory = Path(bin_dir).resolve() if bin_dir else get_toolchain_bin_dir()
    executable = directory / TOOL_REGISTRY[name]["executable"]

    if not executable.is_file():
        raise ToolchainError(
            "Executable for {!r} was not found: {}".format(name, executable)
        )

    return executable


def get_registered_tools() -> Dict[str, Dict[str, Any]]:
    """Return the central tool registry."""
    return TOOL_REGISTRY


def get_tool_options(tool_name: str) -> Dict[str, Any]:
    """Return the option metadata for one registered executable."""
    name = tool_name.strip().lower()

    if name not in TOOL_REGISTRY:
        raise ToolchainError("Unknown registered tool: {!r}".format(tool_name))

    return TOOL_REGISTRY[name].get("options", {})


def get_available_tools(
    bin_dir: Optional[PathLike] = None,
) -> Dict[str, Path]:
    """Return registered executables found in the bundled bin directory."""
    directory = Path(bin_dir).resolve() if bin_dir else get_toolchain_bin_dir()

    return {
        name: directory / metadata["executable"]
        for name, metadata in TOOL_REGISTRY.items()
        if (directory / metadata["executable"]).is_file()
    }


def get_unregistered_executables(
    bin_dir: Optional[PathLike] = None,
) -> List[str]:
    """
    List .exe files in the toolchain bin directory that are not in the
    public registry. This includes GCC internal programs and versioned files.
    """
    directory = Path(bin_dir).resolve() if bin_dir else get_toolchain_bin_dir()

    if not directory.is_dir():
        return []

    registered_filenames = {
        metadata["executable"].lower()
        for metadata in TOOL_REGISTRY.values()
    }

    return sorted(
        path.name
        for path in directory.glob("*.exe")
        if path.name.lower() not in registered_filenames
    )


def detect_toolchain(
    bin_dir: Optional[PathLike] = None,
) -> Dict[str, Any]:
    """Detect registered tools and report missing required executables."""
    directory = Path(bin_dir).resolve() if bin_dir else get_toolchain_bin_dir()
    available = get_available_tools(directory)
    missing = [name for name in REQUIRED_TOOLS if name not in available]

    return {
        "detected": directory.is_dir(),
        "bin_dir": str(directory),
        "available_count": len(available),
        "available_tools": {
            name: str(path) for name, path in available.items()
        },
        "missing_required_tools": missing,
        "unregistered_executables": get_unregistered_executables(directory),
        "valid": directory.is_dir() and not missing,
    }


def validate_toolchain(
    bin_dir: Optional[PathLike] = None,
) -> Dict[str, Any]:
    """Validate the bundled directory and required firmware-build tools."""
    report = detect_toolchain(bin_dir)

    if not report["detected"]:
        raise ToolchainError(
            "ARM GNU Toolchain directory does not exist: {}".format(
                report["bin_dir"]
            )
        )

    if report["missing_required_tools"]:
        raise ToolchainError(
            "Missing required ARM GNU tools: {}".format(
                ", ".join(report["missing_required_tools"])
            )
        )

    return report


# ---------------------------------------------------------------------------
# 3. Version and help/capability discovery
# ---------------------------------------------------------------------------

def _run_process(
    command: Sequence[Union[str, Path]],
    cwd: Optional[PathLike] = None,
    timeout: int = 15,
) -> subprocess.CompletedProcess:
    """Internal subprocess wrapper. Never invokes a shell."""
    working_directory = str(Path(cwd).resolve()) if cwd else None

    try:
        return subprocess.run(
            [str(item) for item in command],
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ToolchainError(
            "Command timed out after {} seconds: {}".format(
                timeout, command[0]
            )
        ) from exc
    except OSError as exc:
        raise ToolchainError(
            "Unable to execute {}: {}".format(command[0], exc)
        ) from exc


def get_tool_version(
    tool_name: str,
    bin_dir: Optional[PathLike] = None,
    timeout: int = 15,
) -> str:
    """Return the first version line reported by a registered executable."""
    executable = get_executable(tool_name, bin_dir)
    result = _run_process([executable, "--version"], timeout=timeout)
    output = (result.stdout or result.stderr).strip()

    if result.returncode != 0 or not output:
        raise ToolchainError(
            "{} --version failed with exit code {}: {}".format(
                tool_name, result.returncode, output
            )
        )

    return output.splitlines()[0]


def get_toolchain_version(
    bin_dir: Optional[PathLike] = None,
    timeout: int = 15,
) -> str:
    """Return the ARM GCC version line."""
    return get_tool_version("gcc", bin_dir=bin_dir, timeout=timeout)


def get_tool_help(
    tool_name: str,
    bin_dir: Optional[PathLike] = None,
    help_argument: str = "--help",
    timeout: int = 20,
) -> str:
    """
    Retrieve the installed executable's help output.

    GNU tools sometimes return a non-zero status for help requests; the
    captured output is returned if present.
    """
    executable = get_executable(tool_name, bin_dir)
    result = _run_process(
        [executable, help_argument],
        timeout=timeout,
    )
    output = "\n".join(
        part for part in (result.stdout.strip(), result.stderr.strip()) if part
    )

    if not output:
        raise ToolchainError(
            "No help output returned by {!r} (exit code {}).".format(
                tool_name, result.returncode
            )
        )

    return output


def get_toolchain_info(
    bin_dir: Optional[PathLike] = None,
) -> ToolchainInfo:
    """Return a structured report of the bundled toolchain installation."""
    directory = Path(bin_dir).resolve() if bin_dir else get_toolchain_bin_dir()
    available = get_available_tools(directory)
    missing = [name for name in REQUIRED_TOOLS if name not in available]

    version = "Unknown"
    if "gcc" in available:
        try:
            version = get_toolchain_version(directory)
        except ToolchainError:
            version = "Unable to determine"

    return ToolchainInfo(
        bin_dir=directory,
        gcc_version=version,
        available_tools=available,
        missing_required_tools=missing,
        unregistered_executables=get_unregistered_executables(directory),
    )


# ---------------------------------------------------------------------------
# 4. Safe executable invocation
# ---------------------------------------------------------------------------

def run_tool(
    tool_name: str,
    arguments: Sequence[object],
    cwd: Optional[PathLike] = None,
    timeout: int = 60,
) -> Dict[str, Any]:
    """
    Execute a registered tool with an argument list.

    `arguments` must be a sequence, for example:
        ["-mcpu=cortex-m4", "-mthumb", "-c", "main.c", "-o", "main.o"]

    Do not pass a shell command string. shell=False is always used.
    A non-zero return code is reported to the caller; it is not hidden.
    """
    if isinstance(arguments, (str, bytes)):
        raise TypeError(
            "arguments must be a sequence of individual arguments, "
            "not one command string"
        )

    executable = get_executable(tool_name)
    command = [str(executable)] + [str(argument) for argument in arguments]
    result = _run_process(command, cwd=cwd, timeout=timeout)

    return {
        "tool": tool_name,
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "success": result.returncode == 0,
    }


# ---------------------------------------------------------------------------
# 5. Registry helpers
# ---------------------------------------------------------------------------

def get_tools_by_category() -> Dict[str, List[str]]:
    """Group registered tool names by their functional category."""
    grouped: Dict[str, List[str]] = {}

    for name, metadata in TOOL_REGISTRY.items():
        grouped.setdefault(metadata["category"], []).append(name)

    return grouped


def get_option_description(
    tool_name: str,
    option_name: str,
) -> Optional[Dict[str, Any]]:
    """Find an option's metadata within a tool's option groups."""
    for options in get_tool_options(tool_name).values():
        if option_name in options:
            return options[option_name]

    return None


def extract_version_number(version_text: str) -> Optional[str]:
    """Extract a numeric version from a version string, when available."""
    match = re.search(r"\b(\d+\.\d+(?:\.\d+)*)\b", version_text)
    return match.group(1) if match else None
