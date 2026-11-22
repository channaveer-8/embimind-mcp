"""EmbiMind MCP server.

The MCP layer exposes ARM GNU toolchain build and ELF-inspection tools,
alongside the existing OpenOCD and GDB managers.
"""

from __future__ import annotations

import atexit
import json
import re
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer

from embimind_mcp import config, target_database
from embimind_mcp.gdb_manager import GDBManager, GDBResult
from embimind_mcp.openocd_manager import openocd_manager
from embimind_mcp.toolchain_manager import validate_toolchain

from embimind_mcp import (
    arm_toolchain,
    compiler,
    linker,
    binary_generator,
    elf_inspector,
)


mcp = MCPServer("EmbiMind")

RESOURCE_DIR = Path(__file__).resolve().parent / "command_catalog"
SYSTEM_GUIDE_PATH = RESOURCE_DIR / "OPENOCD_AI_SYSTEM_GUIDE.md"
COMMAND_REFERENCE_PATH = RESOURCE_DIR / "OPENOCD_COMMAND_REFERENCE.md"
COMMAND_CATALOGUE_PATH = RESOURCE_DIR / "openocd_commands.json"

ARM_TOOLCHAIN_GUIDE_PATH = RESOURCE_DIR / "ARM_TOOLCHAIN_AI_GUIDE.md"
ARM_TOOLCHAIN_REFERENCE_PATH = RESOURCE_DIR / "ARM_TOOLCHAIN_REFERENCE.md"
ARM_TOOLCHAIN_CATALOGUE_PATH = RESOURCE_DIR / "arm_toolchain_commands.json"

gdb_manager = GDBManager(config.GDB_EXE)


def _cleanup_sessions() -> None:
    """Avoid leaving debugger processes behind when the MCP server exits."""
    try:
        gdb_manager.stop()
    except Exception:
        pass
    try:
        openocd_manager.stop_openocd()
    except Exception:
        pass


atexit.register(_cleanup_sessions)


def _gdb_result(result: GDBResult) -> dict[str, Any]:
    """Convert the GDB result dataclass into MCP-friendly data."""
    return {
        "command": result.command,
        "result": result.result,
        "success": result.success,
        "output": result.output,
        "error": result.error,
    }


def _read_resource(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Bundled resource not found: {path.name}")
    return path.read_text(encoding="utf-8")


def _load_catalogue() -> dict[str, Any]:
    return json.loads(_read_resource(COMMAND_CATALOGUE_PATH))


def _requires_openocd_approval(command: str) -> bool:
    """Conservative gate for commands that can alter target flash/configuration."""
    text = command.strip().lower()
    patterns = (
        r"\b(erase|mass_erase|chip_erase|write_image|write_bank|raw_write|program|unlock|protect|option_write)\b",
        r"^(mww|write_memory)\b",
        r"^reset\b",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def _requires_gdb_approval(command: str) -> bool:
    text = command.strip().lower()
    patterns = (
        r"^load\b",
        r"^restore\b",
        r"^set\b",
        r"^monitor\s+.*\b(erase|mass_erase|chip_erase|program|reset|write)\b",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def _validate_single_command(command: str) -> None:
    if not command or not command.strip():
        raise ValueError("Command cannot be empty.")
    # Tcl/GDB command chaining is deliberately disallowed in the generic tools.
    if any(token in command for token in ("\n", "\r", ";", "\x1a")):
        raise ValueError("Submit one command per call; command chaining is not allowed.")


# ---------------------------------------------------------------------------
# Toolchain and target configuration
# ---------------------------------------------------------------------------

@mcp.tool()
def check_toolchain() -> dict:
    """Check that the configured OpenOCD, scripts directory and ARM GDB exist and run."""
    info = validate_toolchain()
    return {
        "status": "valid",
        "openocd": str(info.openocd_path),
        "openocd_scripts": str(info.openocd_scripts_path),
        "gdb": str(info.gdb_path),
        "openocd_version": info.openocd_version,
        "gdb_version": info.gdb_version,
    }


@mcp.tool()
def register_target_configuration(
    board_name: str,
    debugger: str,
    interface_config: str,
    target_config: str,
    transport: str = "swd",
) -> dict:
    """Register a board using paths relative to the OpenOCD scripts directory.

    Example interface_config: interface/stlink.cfg
    Example target_config: target/stm32f4x.cfg
    """
    if transport.lower() not in {"swd", "jtag"}:
        raise ValueError("transport must be 'swd' or 'jtag'.")
    if not board_name.strip() or not debugger.strip():
        raise ValueError("board_name and debugger are required.")

    # Verify paths before persisting the registration.
    scripts_dir = config.OPENOCD_SCRIPTS.resolve()
    verified: dict[str, str] = {}
    for key, value in (
        ("interface_config", interface_config),
        ("target_config", target_config),
    ):
        relative = Path(value)
        if relative.is_absolute():
            raise ValueError(f"{key} must be relative to OpenOCD scripts.")
        resolved = (scripts_dir / relative).resolve()
        try:
            resolved.relative_to(scripts_dir)
        except ValueError as exc:
            raise ValueError(f"{key} escapes the OpenOCD scripts directory.") from exc
        if not resolved.is_file() or resolved.suffix.lower() != ".cfg":
            raise FileNotFoundError(f"OpenOCD config not found: {resolved}")
        verified[key] = relative.as_posix()

    saved = target_database.update_target(
        board_name=board_name.strip(),
        debugger=debugger.strip(),
        interface=verified["interface_config"],
        target=verified["target_config"],
        transport=transport.lower(),
    )
    return {"status": "registered", "board_name": board_name, **saved}


@mcp.tool()
def search_openocd_configs(query: str, limit: int = 50) -> list[dict]:
    """Search bundled interface, target and board OpenOCD .cfg files."""
    return target_database.search_openocd_configs(query, limit)


@mcp.tool()
def get_target_configuration(board_name: str) -> dict:
    """Validate and return a previously registered target configuration."""
    return target_database.verify_target(board_name)


@mcp.tool()
def list_registered_targets() -> list[str]:
    """List board names registered in targets.json."""
    path = target_database.TARGETS_FILE
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("targets.json must contain a JSON object.")
    return sorted(data.keys())


# ---------------------------------------------------------------------------
# OpenOCD lifecycle and command tools
# ---------------------------------------------------------------------------

@mcp.tool()
def start_openocd(board_name: str) -> dict:
    """Start OpenOCD for a registered board and connect to its Tcl RPC port."""
    validate_toolchain()
    return openocd_manager.start_openocd(board_name)


@mcp.tool()
def get_openocd_status() -> dict:
    """Return OpenOCD process and Tcl RPC connection status."""
    return openocd_manager.get_openocd_status()


@mcp.tool()
def stop_openocd() -> dict:
    """Stop the active OpenOCD process."""
    openocd_manager.stop_openocd()
    return {"status": "stopped"}


@mcp.tool()
def search_openocd_commands(query: str) -> list[dict]:
    """Search the bundled OpenOCD command catalogue by name, syntax or description."""
    return openocd_manager.search_commands(query)


@mcp.tool()
def get_openocd_command_mode(command_name: str) -> dict:
    """Ask the running OpenOCD instance whether a command is config or runtime mode."""
    if not re.fullmatch(r"[A-Za-z0-9_ -]{1,100}", command_name.strip()):
        raise ValueError("Invalid OpenOCD command name.")
    return openocd_manager.execute_command(f"command mode {command_name.strip()}")


@mcp.tool()
def execute_openocd_command(
    command: str,
    user_approved: bool = False,
) -> dict:
    """Execute one OpenOCD Tcl command.

    Set user_approved=true only after the user has explicitly approved a
    potentially destructive operation such as flash erase/programming.
    """
    _validate_single_command(command)
    if any(token in command for token in ("[", "]", "$")):
        raise ValueError("Tcl command substitution is not allowed in generic command calls.")
    command_name = command.strip().split(None, 1)[0].lower()
    if command_name in {"source", "exec", "eval", "proc", "rename", "interp", "open"}:
        raise PermissionError(f"The Tcl command '{command_name}' is blocked by EmbiMind.")
    if _requires_openocd_approval(command) and not user_approved:
        raise PermissionError(
            "This command can modify target state or non-volatile memory. "
            "Obtain explicit user approval, then call again with user_approved=true."
        )
    return openocd_manager.execute_command(command)


# ---------------------------------------------------------------------------
# GDB lifecycle, connection and programming
# ---------------------------------------------------------------------------

@mcp.tool()
def start_gdb() -> dict:
    """Start the persistent ARM GDB process in MI2 mode."""
    validate_toolchain()
    pid = gdb_manager.start()
    return {"status": "started", "pid": pid}


@mcp.tool()
def get_gdb_status() -> dict:
    """Return the GDB process status."""
    return gdb_manager.get_status()


@mcp.tool()
def stop_gdb() -> dict:
    """Gracefully stop the GDB process."""
    gdb_manager.stop()
    return {"status": "stopped"}


@mcp.tool()
def load_elf_symbols(elf_path: str) -> dict:
    """Load symbols from an ELF file into GDB; this does not flash the target."""
    return _gdb_result(gdb_manager.load_elf(elf_path))


@mcp.tool()
def connect_gdb(host: str = "127.0.0.1", port: int = 3333) -> dict:
    """Connect GDB to the OpenOCD GDB server."""
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Only a local GDB server connection is allowed.")
    return _gdb_result(gdb_manager.connect(host=host, port=port))


@mcp.tool()
def disconnect_gdb() -> dict:
    """Disconnect GDB from the target without stopping OpenOCD."""
    return _gdb_result(gdb_manager.disconnect())


@mcp.tool()
def flash_elf(user_approved: bool = False) -> dict:
    """Program the currently connected target using the loaded ELF.

    Requires explicit user approval because this changes target flash.
    """
    if not user_approved:
        raise PermissionError("Obtain explicit user approval before programming flash.")
    return _gdb_result(gdb_manager.flash())


@mcp.tool()
def verify_flash() -> dict:
    """Compare the target's programmed sections against the loaded ELF."""
    return _gdb_result(gdb_manager.verify_flash())


# ---------------------------------------------------------------------------
# GDB target control
# ---------------------------------------------------------------------------

@mcp.tool()
def halt_target() -> dict:
    """Halt target execution."""
    return _gdb_result(gdb_manager.halt())


@mcp.tool()
def resume_target() -> dict:
    """Resume target execution."""
    return _gdb_result(gdb_manager.continue_execution())


@mcp.tool()
def step_target() -> dict:
    """Execute one source-level step."""
    return _gdb_result(gdb_manager.step())


@mcp.tool()
def next_target() -> dict:
    """Execute one source-level next operation."""
    return _gdb_result(gdb_manager.next())


@mcp.tool()
def finish_target_function() -> dict:
    """Run until the current function returns."""
    return _gdb_result(gdb_manager.finish())


@mcp.tool()
def reset_target(halt: bool = True, user_approved: bool = False) -> dict:
    """Reset the target, optionally leaving it halted; requires user approval."""
    if not user_approved:
        raise PermissionError("Obtain explicit user approval before resetting the target.")
    return _gdb_result(gdb_manager.reset(halt=halt))


@mcp.tool()
def wait_for_target_stop(timeout: int = 30) -> dict:
    """Wait for an asynchronous GDB target-stop event."""
    if not 1 <= timeout <= 300:
        raise ValueError("timeout must be between 1 and 300 seconds.")
    return {"event": gdb_manager.wait_for_stop(timeout=timeout)}


# ---------------------------------------------------------------------------
# GDB breakpoints, inspection and memory
# ---------------------------------------------------------------------------

@mcp.tool()
def add_breakpoint(location: str) -> dict:
    """Set a breakpoint at a function, file:line or address."""
    return _gdb_result(gdb_manager.add_breakpoint(location))


@mcp.tool()
def remove_breakpoint(breakpoint_id: str) -> dict:
    """Remove a breakpoint by its GDB breakpoint number."""
    if not re.fullmatch(r"\d+(?:\.\d+)?", breakpoint_id):
        raise ValueError("Invalid breakpoint identifier.")
    return _gdb_result(gdb_manager.remove_breakpoint(breakpoint_id))


@mcp.tool()
def list_breakpoints() -> dict:
    """List GDB breakpoints and watchpoints."""
    return _gdb_result(gdb_manager.list_breakpoints())


@mcp.tool()
def add_watchpoint(expression: str, access: str = "write") -> dict:
    """Set a write, read or access watchpoint."""
    return _gdb_result(gdb_manager.add_watchpoint(expression, access))


@mcp.tool()
def get_register_values(format: str = "x") -> dict:
    """Read register values in hexadecimal, octal, binary, decimal or raw format."""
    return _gdb_result(gdb_manager.get_register_values(format))


@mcp.tool()
def get_gdb_info(topic: str) -> dict:
    """Run a GDB info command for the requested topic."""
    if not re.fullmatch(r"[A-Za-z0-9 _-]{1,80}", topic):
        raise ValueError("Invalid GDB info topic.")
    return _gdb_result(gdb_manager.get_info(topic))


@mcp.tool()
def get_registers() -> dict:
    """Read target CPU registers."""
    return _gdb_result(gdb_manager.get_registers())


@mcp.tool()
def read_memory(address: str, count: int = 1, word_size: int = 4) -> dict:
    """Read target memory using GDB."""
    if not re.fullmatch(r"(?:0x[0-9a-fA-F]+|[A-Za-z_][A-Za-z0-9_]*|\$[A-Za-z0-9_]+)", address):
        raise ValueError("Use a hexadecimal address, symbol name or GDB register.")
    if not 1 <= count <= 4096:
        raise ValueError("count must be between 1 and 4096.")
    return _gdb_result(gdb_manager.read_memory(address, count, word_size))


@mcp.tool()
def write_memory(
    address: str,
    value: str,
    word_size: int = 4,
    user_approved: bool = False,
) -> dict:
    """Write target memory. Requires explicit user approval."""
    if not user_approved:
        raise PermissionError("Obtain explicit user approval before writing target memory.")
    if not re.fullmatch(r"0x[0-9a-fA-F]+", address):
        raise ValueError("Memory writes require a literal hexadecimal address.")
    if not re.fullmatch(r"(?:0x[0-9a-fA-F]+|[0-9]+)", value):
        raise ValueError("Memory writes require a literal decimal or hexadecimal value.")
    return _gdb_result(gdb_manager.write_memory(address, value, word_size))


@mcp.tool()
def evaluate_expression(expression: str) -> dict:
    """Evaluate a C expression or symbol in the current GDB context."""
    return _gdb_result(gdb_manager.evaluate(expression))


@mcp.tool()
def get_local_variables() -> dict:
    """Read local variables in the selected stack frame."""
    return _gdb_result(gdb_manager.get_local_variables())


@mcp.tool()
def get_backtrace() -> dict:
    """Read the current call stack."""
    return _gdb_result(gdb_manager.get_backtrace())


@mcp.tool()
def get_stack_arguments() -> dict:
    """Read arguments for stack frames."""
    return _gdb_result(gdb_manager.get_stack_arguments())


@mcp.tool()
def get_source_listing() -> dict:
    """List source around the current execution location."""
    return _gdb_result(gdb_manager.get_source())


@mcp.tool()
def disassemble(location: str = "$pc") -> dict:
    """Disassemble code at the supplied location."""
    _validate_single_command(location)
    if not re.fullmatch(r"[A-Za-z0-9_.$:+-]+", location):
        raise ValueError("Invalid disassembly location.")
    return _gdb_result(gdb_manager.disassemble(location))


@mcp.tool()
def get_threads() -> dict:
    """List threads known to GDB."""
    return _gdb_result(gdb_manager.get_threads())


@mcp.tool()
def get_target_state() -> dict:
    """Return GDB's current target execution state."""
    return _gdb_result(gdb_manager.get_target_state())


@mcp.tool()
def get_gdb_event(timeout: float = 0.1) -> dict:
    """Read one queued GDB asynchronous event, if available."""
    if not 0 <= timeout <= 10:
        raise ValueError("timeout must be between 0 and 10 seconds.")
    return {"event": gdb_manager.get_event(timeout=timeout)}


@mcp.tool()
def execute_gdb_command(
    command: str,
    user_approved: bool = False,
) -> dict:
    """Execute one GDB CLI command through GDB/MI.

    Potentially destructive commands require user_approved=true after
    explicit user approval.
    """
    _validate_single_command(command)
    if _requires_gdb_approval(command) and not user_approved:
        raise PermissionError(
            "This GDB command can modify target state or flash. "
            "Obtain explicit user approval, then call again with user_approved=true."
        )
    return _gdb_result(gdb_manager.execute_command(command))


@mcp.tool()
def execute_gdb_mi_command(
    command: str,
    user_approved: bool = False,
) -> dict:
    """Execute a GDB/MI command, for advanced GDB integration."""
    _validate_single_command(command)
    normalized = command.strip().lower()
    if not normalized.startswith("-"):
        raise ValueError("GDB/MI commands must begin with '-'.")
    if normalized.startswith((
        "-interpreter-exec",
        "-target-download",
        "-data-write-memory",
        "-data-write-memory-bytes",
    )) and not user_approved:
        raise PermissionError(
            "This MI command can execute arbitrary GDB CLI or modify target state. "
            "Obtain explicit user approval first."
        )
    return _gdb_result(gdb_manager.execute_mi(command))




# ---------------------------------------------------------------------------
# ARM GNU toolchain, firmware build and ELF inspection
# ---------------------------------------------------------------------------

@mcp.tool()
def check_arm_toolchain() -> dict:
    """Detect and validate the configured ARM GNU toolchain."""
    info = arm_toolchain.get_toolchain_info()
    if hasattr(info, "__dataclass_fields__"):
        result = {
            key: str(value) if isinstance(value, Path) else value
            for key, value in vars(info).items()
        }
        return result
    if isinstance(info, dict):
        return info
    return {"info": str(info)}


@mcp.tool()
def list_arm_tools() -> list:
    """List ARM GNU toolchain executables detected in the configured bin directory."""
    return arm_toolchain.get_available_tools()


@mcp.tool()
def compile_c(
    source: str,
    output: str | None = None,
    flags: list[str] | None = None,
    include_dirs: list[str] | None = None,
    defines: list[str] | None = None,
    timeout: int = 60,
) -> dict:
    """Compile one C source file into an object file."""
    return compiler.compile_c(
        source=source,
        output=output,
        flags=flags,
        include_dirs=include_dirs,
        defines=defines,
        timeout=timeout,
    )


@mcp.tool()
def compile_cpp(
    source: str,
    output: str | None = None,
    flags: list[str] | None = None,
    include_dirs: list[str] | None = None,
    defines: list[str] | None = None,
    timeout: int = 60,
) -> dict:
    """Compile one C++ source file into an object file."""
    return compiler.compile_cpp(
        source=source,
        output=output,
        flags=flags,
        include_dirs=include_dirs,
        defines=defines,
        timeout=timeout,
    )


@mcp.tool()
def preprocess_source(
    source: str,
    output: str | None = None,
    flags: list[str] | None = None,
    include_dirs: list[str] | None = None,
    defines: list[str] | None = None,
    timeout: int = 60,
) -> dict:
    """Run the C/C++ preprocessor on a source file."""
    return compiler.preprocess(
        source=source,
        output=output,
        flags=flags,
        include_dirs=include_dirs,
        defines=defines,
        timeout=timeout,
    )


@mcp.tool()
def link_elf(
    object_files: list[str],
    output: str,
    linker_script: str | None = None,
    flags: list[str] | None = None,
    library_dirs: list[str] | None = None,
    libraries: list[str] | None = None,
    map_file: str | None = None,
    gc_sections: bool = False,
    print_memory_usage: bool = False,
    timeout: int = 120,
) -> dict:
    """Link object files into an ELF firmware image."""
    return linker.link_elf(
        object_files=object_files,
        output=output,
        linker_script=linker_script,
        flags=flags,
        library_dirs=library_dirs,
        libraries=libraries,
        map_file=map_file,
        gc_sections=gc_sections,
        print_memory_usage=print_memory_usage,
        timeout=timeout,
    )


@mcp.tool()
def create_static_library(
    object_files: list[str],
    output: str,
    flags: str = "rcs",
    timeout: int = 60,
) -> dict:
    """Create a static library archive from object files."""
    return linker.create_static_library(
        object_files=object_files,
        output=output,
        flags=flags,
        timeout=timeout,
    )


@mcp.tool()
def elf_to_bin(
    elf_file: str,
    output_file: str | None = None,
    flags: list[str] | None = None,
    timeout: int = 60,
) -> dict:
    """Convert an ELF firmware image into a raw binary."""
    return binary_generator.elf_to_bin(
        elf_file=elf_file,
        output_file=output_file,
        flags=flags,
        timeout=timeout,
    )


@mcp.tool()
def elf_to_hex(
    elf_file: str,
    output_file: str | None = None,
    flags: list[str] | None = None,
    timeout: int = 60,
) -> dict:
    """Convert an ELF firmware image into Intel HEX format."""
    return binary_generator.elf_to_hex(
        elf_file=elf_file,
        output_file=output_file,
        flags=flags,
        timeout=timeout,
    )


@mcp.tool()
def convert_elf(
    elf_file: str,
    output_file: str,
    output_format: str,
    flags: list[str] | None = None,
    timeout: int = 60,
) -> dict:
    """Convert an ELF image to a supported objcopy output format."""
    return binary_generator.convert_elf(
        elf_file=elf_file,
        output_file=output_file,
        output_format=output_format,
        flags=flags,
        timeout=timeout,
    )


@mcp.tool()
def inspect_elf_header(elf_file: str) -> dict:
    """Inspect ELF file header information."""
    return elf_inspector.inspect_elf_header(elf_file)


@mcp.tool()
def inspect_elf_sections(elf_file: str) -> dict:
    """List sections in an ELF firmware image."""
    return elf_inspector.inspect_sections(elf_file)


@mcp.tool()
def inspect_elf_segments(elf_file: str) -> dict:
    """Inspect ELF program segments and load information."""
    return elf_inspector.inspect_segments(elf_file)


@mcp.tool()
def inspect_elf_symbols(
    elf_file: str,
    demangle: bool = True,
    only_external: bool = False,
) -> dict:
    """Inspect symbols in an ELF firmware image."""
    return elf_inspector.inspect_symbols(
        elf_file=elf_file,
        demangle=demangle,
        only_external=only_external,
    )


@mcp.tool()
def inspect_disassembly(
    elf_file: str,
    source_interleaved: bool = False,
    all_sections: bool = False,
) -> dict:
    """Disassemble an ELF image, optionally interleaving source code."""
    return elf_inspector.inspect_disassembly(
        elf_file=elf_file,
        source_interleaved=source_interleaved,
        all_sections=all_sections,
    )


@mcp.tool()
def inspect_memory_usage(elf_file: str) -> dict:
    """Report ELF section memory usage using the ARM size utility."""
    return elf_inspector.inspect_memory_usage(elf_file)


@mcp.tool()
def inspect_all_elf_headers(elf_file: str) -> dict:
    """Inspect all ELF header and metadata information."""
    return elf_inspector.inspect_all_headers(elf_file)


@mcp.tool()
def address_to_source(
    elf_file: str,
    addresses: list[str],
    functions: bool = True,
    demangle: bool = True,
    timeout: int = 30,
) -> dict:
    """Map firmware addresses to source files and line numbers."""
    return elf_inspector.address_to_source(
        elf_file=elf_file,
        addresses=addresses,
        functions=functions,
        demangle=demangle,
        timeout=timeout,
    )


@mcp.tool()
def inspect_file_format(input_file: str) -> dict:
    """Identify the file format and architecture of an object or firmware file."""
    return elf_inspector.inspect_file_format(input_file)


# ---------------------------------------------------------------------------
# MCP resources
# --------------------------------------------------------------------------------------

@mcp.resource("embimind://openocd/ai-system-guide", mime_type="text/markdown")
def openocd_ai_system_guide() -> str:
    """OpenOCD architecture and operational guidance for the AI assistant."""
    return _read_resource(SYSTEM_GUIDE_PATH)


@mcp.resource("embimind://openocd/command-reference", mime_type="text/markdown")
def openocd_command_reference() -> str:
    """Detailed OpenOCD command reference."""
    return _read_resource(COMMAND_REFERENCE_PATH)


@mcp.resource("embimind://openocd/command-catalogue", mime_type="application/json")
def openocd_command_catalogue() -> str:
    """Structured OpenOCD command and driver catalogue."""
    return _read_resource(COMMAND_CATALOGUE_PATH)


@mcp.resource(
    "embimind://toolchain/ai-guide",
    name="ARM Toolchain AI System Guide",
    description=(
        "Instructions for using EmbiMind's ARM GNU build tools. Covers "
        "build-stage order, tool selection, artifact checks and safe operation."
    ),
    mime_type="text/markdown",
)
def arm_toolchain_ai_guide() -> str:
    """Return the ARM toolchain operating guide for AI assistants."""
    return _read_resource(ARM_TOOLCHAIN_GUIDE_PATH)


@mcp.resource(
    "embimind://toolchain/reference",
    name="ARM GNU Toolchain Reference",
    description=(
        "Technical reference for ARM GCC, G++, linker, binutils, supported "
        "options, output formats and common firmware build operations."
    ),
    mime_type="text/markdown",
)
def arm_toolchain_reference() -> str:
    """Return the ARM GNU toolchain technical reference."""
    return _read_resource(ARM_TOOLCHAIN_REFERENCE_PATH)


@mcp.resource(
    "embimind://toolchain/catalogue",
    name="ARM Toolchain MCP Catalogue",
    description=(
        "Structured catalogue mapping EmbiMind firmware build and ELF "
        "inspection MCP tools to their purpose, arguments and dependencies."
    ),
    mime_type="application/json",
)
def arm_toolchain_catalogue() -> str:
    """Return the structured ARM toolchain MCP catalogue."""
    return _read_resource(ARM_TOOLCHAIN_CATALOGUE_PATH)


# ---------------------------------------------------------------------------
# MCP prompts
# ---------------------------------------------------------------------------

@mcp.prompt()
def embimind_system_guidance() -> str:
    """Core operating instructions for an AI assistant using EmbiMind."""
    return """
You are using EmbiMind, an MCP interface for embedded target connection,
programming and debugging through OpenOCD and ARM GDB.

Use the OpenOCD AI System Guide, Command Reference and JSON Catalogue as
the primary technical references. Do not invent command syntax or assume
that a catalogue entry exists in the installed OpenOCD build.

Operating rules:
1. Distinguish configuration-stage commands from runtime commands.
   Configuration-only commands must be applied before OpenOCD initialization.
2. Register and validate the target configuration before starting OpenOCD.
3. Start OpenOCD once and reuse its persistent session. GDB connects to
   OpenOCD's GDB server; do not launch a second OpenOCD instance through GDB.
4. Check process, RPC and target status before issuing dependent operations.
5. Ask the user to identify the board, MCU, debug probe and transport when
   those details are ambiguous. Do not infer an exact board from an MCU alone.
6. Obtain explicit user approval before flash programming/erasing, target
   memory writes, reset operations that disrupt execution, or other destructive
   operations. Only set user_approved=true after that approval.
7. Do not claim success unless the tool response confirms it.
8. Separate observed output, interpretation, hypotheses and recommendations.
9. Firmware compilation is performed by the user's IDE/build system. EmbiMind
   handles artifact loading, target programming and debugging; it does not
   compile firmware.
10. Report exact artifact paths and target configuration used.
"""


@mcp.prompt()
def firmware_build_workflow(
    source_files: str,
    target_architecture: str,
    linker_script: str = "",
) -> str:
    """Guide a firmware build using the ARM GNU toolchain."""
    return f"""
Build firmware using EmbiMind.

Source files: {source_files}
Target architecture: {target_architecture}
Linker script: {linker_script or "Not specified"}

Consult the ARM Toolchain AI Guide, Reference and Catalogue.
Check toolchain availability, compile sources, link object files,
inspect the ELF, and generate BIN/HEX only when requested.
Verify every stage and report errors and artifact paths.
Ask for missing target-specific settings. Do not flash the target.
"""


@mcp.prompt()
def connect_target_workflow(
    board_name: str,
    debugger: str,
    transport: str = "swd",
) -> str:
    """Guide the assistant through registering and connecting a target."""
    return f"""
Connect the following embedded target using EmbiMind.

Board: {board_name}
Debug probe: {debugger}
Transport: {transport}

Workflow:
1. Confirm that the board name, MCU and probe combination is unambiguous.
2. Search the bundled OpenOCD scripts for the appropriate interface and
   target configuration files. Prefer a board configuration only when it
   is appropriate; avoid loading duplicate interface/target configurations.
3. Register the selected relative config paths with
   register_target_configuration.
4. Call get_target_configuration to validate the files.
5. Check the toolchain, then call start_openocd.
6. Check get_openocd_status and report the detected target and any errors.
7. Do not silently download missing scripts or change hardware configuration.
"""


@mcp.prompt()
def flash_firmware_workflow(
    firmware_path: str,
    board_name: str,
) -> str:
    """Guide a safe firmware programming and verification workflow."""
    return f"""
Program and verify firmware on the requested target.

Firmware ELF: {firmware_path}
Board: {board_name}

Workflow:
1. Confirm the ELF exists and is intended for this exact target.
2. Confirm the target is connected and the GDB server is available.
3. Start GDB, load ELF symbols and connect to the OpenOCD GDB server.
4. Before programming, explain that flash contents will be modified and ask
   the user for explicit approval.
5. Only after approval, call flash_elf(user_approved=true).
6. Call verify_flash and report whether section comparison succeeded.
7. Reset/run only when the user authorizes the resulting target-state change.
8. Do not report programming success if GDB returns an error.
"""


@mcp.prompt()
def diagnose_target_workflow(
    symptom: str,
    board_name: str = "unspecified",
) -> str:
    """Guide evidence-based diagnosis of an embedded target."""
    return f"""
Diagnose the reported embedded target issue.

Board: {board_name}
Symptom: {symptom}

Collect evidence before concluding:
1. Check OpenOCD and GDB process status.
2. Check Tcl RPC/GDB connection and target state.
3. Inspect relevant OpenOCD output, registers, backtrace, breakpoints,
   memory and source context as appropriate.
4. Consult the OpenOCD system guide and command catalogue before selecting
   OpenOCD-specific commands.
5. Distinguish observed facts from interpretations and hypotheses.
6. Recommend the next diagnostic action and explain its expected result.
7. Do not issue destructive commands without explicit user approval.
"""


@mcp.prompt()
def openocd_command_guidance(topic: str) -> str:
    """Explain OpenOCD commands using the bundled reference resources."""
    return f"""
The user wants guidance about this OpenOCD topic: {topic}

Search the bundled command catalogue and consult the command reference.
Explain exact syntax, purpose, execution class and preconditions. Identify
whether the command is configuration-only or suitable for runtime Tcl RPC.
A runtime-candidate entry is not proof that the installed build supports it.
Do not execute commands unless the user requests execution. Require explicit
approval for operations that modify flash, target memory or hardware state.
"""


def main() -> None:
    """Run the EmbiMind MCP server over stdio."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
