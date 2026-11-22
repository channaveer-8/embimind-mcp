# EmbiMind — ARM GNU Toolchain AI Guide

## Purpose

Use this guide when assisting with embedded firmware build and inspection tasks through EmbiMind. The ARM GNU Toolchain MCP tools cover source preprocessing, compilation, linking, binary conversion, and ELF inspection. OpenOCD and GDB hardware-debugging operations are separate parts of EmbiMind.

The goal is to produce a reproducible firmware artifact and explain what was built. Do not claim that firmware was flashed or tested on hardware unless the corresponding hardware operation actually completed successfully.

## Operating rules

1. **Discover before building.** Call `check_arm_toolchain` first. If required tools are missing, report the missing tools and stop the build rather than pretending the toolchain is ready.
2. **Use the target details supplied by the user.** Do not guess the MCU, CPU, FPU, ABI, clock, memory map, linker script, startup code, or board configuration.
3. **Preserve user configuration.** Inspect existing build flags, include paths, macro definitions, linker scripts, startup files, and source layout before proposing replacements.
4. **Use explicit arguments.** Pass flags as individual list entries, not as a shell command string. Paths should be passed as paths, not embedded into a command string.
5. **Build in stages.** Preprocess or compile source files, link object files into an ELF, then generate BIN/HEX only when requested or required by the target workflow.
6. **Inspect the ELF before delivery.** Check its header, sections, segments, symbols, and memory usage as appropriate. A successful linker exit code alone does not prove that the memory layout is correct.
7. **Report actual results.** Include each operation's success status, output path, return code, and relevant diagnostics. Do not hide compiler or linker errors.
8. **Do not silently change source code.** If a build fails, explain the first actionable error and suggest a focused correction. Modify source only when the user asks for that change or explicitly approves it.
9. **Do not invent a flash address.** The linker script and target memory map determine placement. Never infer a flash offset from a BIN file name or size.
10. **Separate build from programming.** Creating an ELF/BIN/HEX does not flash a device. Use the OpenOCD/GDB workflow for hardware operations, with explicit confirmation for destructive or irreversible actions where required by the server.

## Toolchain discovery

Start with:

- `check_arm_toolchain` — reports the configured ARM GNU toolchain, GCC version, available tools, and missing required tools.
- `list_arm_tools` — lists registered executables found by the current toolchain configuration.

The required tool set currently includes `gcc`, `g++`, `as`, `ld`, `ar`, `objcopy`, `objdump`, `readelf`, `nm`, `size`, and `gdb`.

If discovery fails:
- Report the exact missing tool names.
- Do not continue with compilation or linking.
- Ask the user to install or point EmbiMind to a compatible ARM GNU bare-metal toolchain.
- Do not assume a host-native compiler is an acceptable substitute for `arm-none-eabi-*`.

## Build workflow

### 1. Establish the target configuration

Before selecting flags, identify:
- MCU / CPU core (for example, Cortex-M4).
- Thumb/ARM instruction mode, where applicable.
- FPU and floating-point ABI, where applicable.
- C and C++ language standards.
- Optimization and debug-information requirements.
- Startup and system initialization files.
- Linker script and memory regions.
- Required libraries and runtime policy (`newlib`, `nosys`, `nano`, or project-specific specs).

If any of these affect correctness and are unknown, ask one focused clarification instead of guessing.

### 2. Preprocess when useful

Use `preprocess_source` to inspect macro expansion, include resolution, and conditional compilation.

Example parameters:
- `source`: `src/main.c`
- `output`: `build/main.i`
- `flags`: `["-mcpu=cortex-m4", "-mthumb"]`
- `include_dirs`: `["include", "drivers/include"]`
- `defines`: `["USE_HAL_DRIVER", "STM32F411xE"]`

The tool adds `-E`, include (`-I`) and define (`-D`) arguments. Do not add a second `-E` unless there is a specific reason.

### 3. Compile source files

Use:
- `compile_c` for one C source file.
- `compile_cpp` for one C++ source file.

Both create an object file (`.o`) and accept:
- `source` (required)
- `output` (optional; defaults to the source path with `.o`)
- `flags` (optional list of compiler arguments)
- `include_dirs` (optional list of include directories)
- `defines` (optional list of preprocessor definitions)
- `timeout` (seconds; default 60)

Typical Cortex-M flags, only when confirmed for the selected MCU:
```text
-mcpu=cortex-m4
-mthumb
-mfpu=fpv4-sp-d16
-mfloat-abi=hard
-std=c11
-ffunction-sections
-fdata-sections
-Wall
-Wextra
-g
-Og
```

The FPU and ABI flags must match the MCU and all linked libraries. Do not copy the example flags blindly.

The current MCP layer exposes C and C++ compilation and preprocessing. The lower-level Python compiler module also has an assembly helper, but there is no corresponding `compile_assembly` MCP tool in the current server interface.

### 4. Link object files into ELF

Use `link_elf` after all required object files and libraries are available.

Important parameters:
- `object_files`: list of existing `.o` files (required).
- `output`: ELF output path (required).
- `linker_script`: optional linker script path.
- `flags`: additional GCC driver/linker arguments.
- `library_dirs`: optional library search directories.
- `libraries`: library names without the `lib` prefix or extension (for example, `m`).
- `map_file`: optional linker map output path.
- `gc_sections`: enables `-Wl,--gc-sections`.
- `print_memory_usage`: enables `-Wl,--print-memory-usage`.
- `timeout`: seconds (default 120).

The linker wrapper uses the GCC driver for the final link. This is intentional: GCC supplies the target runtime and linker support. Do not replace it with a direct `ld` invocation unless the project explicitly requires that workflow.

Check:
- All required object files are present.
- Exactly the intended linker script is used.
- Startup/vector-table sections are retained.
- Linker symbols and memory regions match the device.
- Libraries use the same CPU/FPU/ABI settings.
- There are no unresolved symbols or region overflow errors.

### 5. Generate output images

- `elf_to_bin` converts ELF to raw binary (`binary` output format). Default output replaces the ELF suffix with `.bin`.
- `elf_to_hex` converts ELF to Intel HEX (`ihex` output format). Default output replaces the ELF suffix with `.hex`.
- `convert_elf` supports the explicitly validated formats `binary`, `ihex`, `srec`, and `elf`.

Use the format required by the flashing/programming process. A raw BIN does not carry the ELF's load-address metadata; obtain the correct programming address from the linker script, board configuration, or target documentation.

Do not describe Intel HEX as a raw binary. Do not assume every programmer accepts every format.

### 6. Inspect and validate the ELF

Use the smallest inspection tool that answers the question:

| Need | MCP tool |
|---|---|
| ELF class, endianness, machine, entry point | `inspect_elf_header` |
| Section names, addresses, sizes, flags | `inspect_elf_sections` |
| Loadable program segments | `inspect_elf_segments` |
| Symbol table | `inspect_elf_symbols` |
| Assembly / mixed source disassembly | `inspect_disassembly` |
| Section size summary | `inspect_memory_usage` |
| Broad ELF metadata dump | `inspect_all_elf_headers` |
| Map code addresses to source locations | `address_to_source` |
| Object/ELF file format and architecture | `inspect_file_format` |

For C++ symbols, `inspect_elf_symbols` demangles names by default. Set `only_external` to true when only global/external symbols are needed.

For disassembly:
- `source_interleaved=true` requests source lines alongside disassembly (requires suitable debug information).
- `all_sections=true` uses objdump's all-sections disassembly mode; otherwise it disassembles code sections.

For address lookup, provide addresses as strings (for example, `["0x08001234", "0x08001280"]`). Debug information and matching source files improve the result.

## Recommended build sequence

```text
check_arm_toolchain
        |
        v
preprocess_source (optional)
        |
        v
compile_c / compile_cpp (for each source file)
        |
        v
link_elf
        |
        +------> inspect_elf_header
        +------> inspect_elf_sections
        +------> inspect_elf_segments
        +------> inspect_memory_usage
        |
        v
elf_to_bin / elf_to_hex (as required)
        |
        v
Report artifact paths and validation results
```

## Failure handling

- **Tool not found:** report the missing executable and check the configured toolchain location and PATH fallback.
- **Compilation failure:** report source file, compiler diagnostics, and the failing command arguments returned by the tool.
- **Link failure:** inspect undefined symbols, missing libraries, linker-script paths, and memory-region overflow.
- **Unexpected ELF architecture:** compare the ELF machine/class with the requested MCU architecture and compiler flags.
- **Unexpected memory usage:** inspect sections and the linker map; do not estimate memory use from the BIN file alone.
- **BIN/HEX conversion failure:** verify that the ELF exists and that the requested output format is supported.

## Cross-platform packaging contract

EmbiMind exposes the same MCP tool names, parameters, and result structure on Windows and Linux. Platform-specific executable binaries live in the replaceable `toolchain/` directory; the Python MCP interface should not fork by operating system.

The intended executable lookup order is:
1. Explicit environment-variable override, when configured.
2. Bundled executable in the package's `toolchain/` directory.
3. Executable available through the system `PATH`.

The executable resolver must account for platform-specific filenames (`.exe` on Windows and no `.exe` suffix on Linux). Keep this behavior inside toolchain discovery; compiler, linker, binary-generation, and ELF-inspection callers should use logical tool names such as `gcc`, `objcopy`, and `readelf`.

This is the agreed packaging contract. If the current resolver does not yet implement all three lookup levels, treat that as an implementation task—not as evidence that the fallback already works.

## Scope and limitations

- The current MCP build tools operate on individual source files and object files. They do not discover a project build system or automatically parse CMake, Make, IDE, or vendor project files.
- They do not automatically generate startup code, linker scripts, device headers, or board support packages.
- They do not automatically flash or verify firmware on hardware.
- The registered option metadata is curated guidance, not a complete GNU manual. The installed executable's help output and actual exit status remain authoritative.
- Toolchain version and target support depend on the binaries included in the selected package.
