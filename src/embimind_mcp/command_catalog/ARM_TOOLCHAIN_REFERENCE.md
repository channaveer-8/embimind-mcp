# EmbiMind — ARM GNU Toolchain Reference

## 1. Scope

This reference documents the ARM GNU bare-metal toolchain integration exposed by EmbiMind.

- Tool prefix: `arm-none-eabi-`
- Typical outputs: object files (`.o`), ELF firmware (`.elf`), raw binary (`.bin`), Intel HEX (`.hex`), and static archives (`.a`).
- Target architecture and ABI are selected by compiler/linker flags and the target's linker script.
- OpenOCD is responsible for target connection/programming operations; this reference covers build and ELF utilities.

## 2. Registered executables

Logical registry names are used by EmbiMind. The actual executable filename is platform/package dependent.

| Logical name | Executable family | Category | Main purpose |
|---|---|---|---|
| `gcc` | `arm-none-eabi-gcc` | Compiler | C compiler driver and final link driver |
| `g++` | `arm-none-eabi-g++` | Compiler | C++ compiler driver |
| `cpp` | `arm-none-eabi-cpp` | Preprocessor | C/C++ preprocessing |
| `as` | `arm-none-eabi-as` | Assembler | GNU assembler |
| `ld` | `arm-none-eabi-ld` | Linker | GNU linker (available for direct use where needed) |
| `ld.bfd` | `arm-none-eabi-ld.bfd` | Linker | BFD linker |
| `ar` | `arm-none-eabi-ar` | Archive | Create and manage static archives |
| `ranlib` | `arm-none-eabi-ranlib` | Archive | Generate archive symbol index |
| `gcc-ar` | `arm-none-eabi-gcc-ar` | Archive | GCC-aware archive wrapper, including LTO integration |
| `gcc-ranlib` | `arm-none-eabi-gcc-ranlib` | Archive | GCC-aware ranlib wrapper |
| `objcopy` | `arm-none-eabi-objcopy` | Binary | Convert/copy object and firmware formats |
| `strip` | `arm-none-eabi-strip` | Binary | Remove symbol/debug information |
| `objdump` | `arm-none-eabi-objdump` | Inspection | Disassembly and object-file information |
| `readelf` | `arm-none-eabi-readelf` | Inspection | ELF headers, sections, segments, and metadata |
| `nm` | `arm-none-eabi-nm` | Inspection | Symbol listing |
| `size` | `arm-none-eabi-size` | Inspection | Section-size summary |
| `addr2line` | `arm-none-eabi-addr2line` | Inspection | Address-to-source lookup |
| `strings` | `arm-none-eabi-strings` | Inspection | Printable strings in binary/object files |
| `c++filt` | `arm-none-eabi-c++filt` | Inspection | Demangle C++ symbol names |
| `elfedit` | `arm-none-eabi-elfedit` | Inspection | Update ELF header attributes |
| `gcov` | `arm-none-eabi-gcov` | Coverage | GCC coverage data processing |
| `gcov-dump` | `arm-none-eabi-gcov-dump` | Coverage | Dump coverage-file contents |
| `gcov-tool` | `arm-none-eabi-gcov-tool` | Coverage | Manipulate coverage data |
| `gprof` | `arm-none-eabi-gprof` | Profiling | Profile analysis |
| `lto-dump` | `arm-none-eabi-lto-dump` | LTO | Inspect GCC LTO object data |
| `gdb` | `arm-none-eabi-gdb` | Debugger | GNU debugger for ARM bare-metal targets |
| `gdb-py` | `arm-none-eabi-gdb-py` | Debugger | Python-enabled GDB build, if packaged |

Not every registered executable is required for a basic build. EmbiMind's current required-tool validation set is:

`gcc`, `g++`, `as`, `ld`, `ar`, `objcopy`, `objdump`, `readelf`, `nm`, `size`, `gdb`.

The exact executable filenames must be resolved for the host platform. Do not hard-code `.exe` in cross-platform caller code.

## 3. MCP tool reference

The following are the ARM toolchain MCP tools currently registered in `main.py`.

### Discovery

#### `check_arm_toolchain()`
Checks the configured toolchain and returns its information, including GCC version, available tools, missing required tools, and related discovery details.

#### `list_arm_tools()`
Lists registered executables detected in the configured toolchain bin directory.

### Source preparation and compilation

#### `preprocess_source(source, output=None, flags=None, include_dirs=None, defines=None, timeout=60)`
Runs the C/C++ preprocessor and writes a `.i` file by default.

- `source`: existing source file.
- `output`: optional output path.
- `flags`: list of compiler arguments.
- `include_dirs`: directories passed as `-I`.
- `defines`: macro definitions passed as `-D`.
- `timeout`: process timeout in seconds.

#### `compile_c(source, output=None, flags=None, include_dirs=None, defines=None, timeout=60)`
Compiles one C source file into an object file. Default output is the source path with `.o`.

#### `compile_cpp(source, output=None, flags=None, include_dirs=None, defines=None, timeout=60)`
Compiles one C++ source file into an object file. Default output is the source path with `.o`.

The current MCP interface does not expose the lower-level Python module's `compile_assembly` helper as an MCP tool.

### Linking and archives

#### `link_elf(object_files, output, linker_script=None, flags=None, library_dirs=None, libraries=None, map_file=None, gc_sections=False, print_memory_usage=False, timeout=120)`
Links existing object files into an ELF firmware image using the GCC driver.

- `object_files`: non-empty list of object-file paths.
- `output`: ELF output path.
- `linker_script`: optional linker script, passed as `-T`.
- `flags`: additional GCC/linker arguments.
- `library_dirs`: directories passed as `-L`.
- `libraries`: names passed as `-l` (without `lib` prefix or extension).
- `map_file`: optional map-file path.
- `gc_sections`: adds `-Wl,--gc-sections`.
- `print_memory_usage`: adds `-Wl,--print-memory-usage`.
- `timeout`: default 120 seconds.

#### `create_static_library(object_files, output, flags="rcs", timeout=60)`
Creates a static archive (`.a`) using `ar`.

The lower-level Python module also exposes `index_static_library(archive)`, but there is no matching MCP tool in the current server interface.

### Binary conversion

#### `elf_to_bin(elf_file, output_file=None, flags=None, timeout=60)`
Converts an ELF file to raw binary using `objcopy -O binary`. Default output uses the `.bin` suffix.

#### `elf_to_hex(elf_file, output_file=None, flags=None, timeout=60)`
Converts an ELF file to Intel HEX using `objcopy -O ihex`. Default output uses the `.hex` suffix.

#### `convert_elf(elf_file, output_file, output_format, flags=None, timeout=60)`
Converts ELF to one of the formats accepted by the current wrapper:
- `binary`
- `ihex`
- `srec`
- `elf`

The installed `objcopy` must support the requested format. The wrapper validates the format name before execution.

### ELF and object inspection

#### `inspect_elf_header(elf_file)`
Displays ELF file header information using `readelf -h`.

#### `inspect_elf_sections(elf_file)`
Displays section headers using `readelf -S`.

#### `inspect_elf_segments(elf_file)`
Displays program headers/segments using `readelf -l`.

#### `inspect_elf_symbols(elf_file, demangle=True, only_external=False)`
Lists symbols using `nm`. `demangle` enables `-C`; `only_external` enables `-g`.

#### `inspect_disassembly(elf_file, source_interleaved=False, all_sections=False)`
Uses `objdump`. Default disassembly is `-d`; `all_sections` selects `-D`; `source_interleaved` adds `-S`.

#### `inspect_memory_usage(elf_file)`
Uses `size -B` for a Berkeley-style section-size summary.

#### `inspect_all_elf_headers(elf_file)`
Uses `readelf -a` to display broad ELF metadata.

#### `address_to_source(elf_file, addresses, functions=True, demangle=True, timeout=30)`
Uses `addr2line -e`. Addresses must be supplied as a list of strings. `functions` adds `-f`; `demangle` adds `-C`.

#### `inspect_file_format(input_file)`
Uses `objdump -f` to report object-file format and architecture information.

## 4. Common compiler and linker options

These are common GNU options, not an exhaustive list. Exact support depends on the installed compiler version and target.

| Option | Meaning |
|---|---|
| `-mcpu=<cpu>` | Select target CPU/core |
| `-march=<arch>` | Select target architecture |
| `-mthumb` | Generate Thumb instructions |
| `-mfpu=<fpu>` | Select FPU instruction set |
| `-mfloat-abi=<soft\|softfp\|hard>` | Select floating-point calling convention |
| `-O0`, `-Og`, `-O1`, `-O2`, `-O3`, `-Os` | Optimization level |
| `-g` | Generate debug information |
| `-std=c11` | Select C language standard |
| `-std=c++17` | Select C++ language standard |
| `-Wall`, `-Wextra` | Enable common warning groups |
| `-Werror` | Treat warnings as errors |
| `-I <dir>` | Add include directory |
| `-D <name>[=<value>]` | Define preprocessor macro |
| `-c` | Compile/assemble without linking |
| `-E` | Preprocess only |
| `-S` | Compile to assembly |
| `-T <script>` | Select linker script |
| `-L <dir>` | Add library search directory |
| `-l<name>` | Link library |
| `-Wl,<options>` | Forward options to linker |
| `-ffunction-sections` | Place functions in individual sections |
| `-fdata-sections` | Place data items in individual sections |
| `-Wl,--gc-sections` | Remove unused input sections |
| `-Wl,-Map=<file>` | Generate linker map |

### Cortex-M example (illustrative only)

```text
-mcpu=cortex-m4
-mthumb
-mfpu=fpv4-sp-d16
-mfloat-abi=hard
-g
-Og
-ffunction-sections
-fdata-sections
-Wall
-Wextra
```

Confirm the exact MCU, FPU, ABI, and library build settings before using these options. A hard-float/soft-float mismatch can cause link failures or ABI incompatibility.

## 5. Typical build sequence

```text
C/C++ source files
       |
       v
preprocess_source (optional)
       |
       v
compile_c / compile_cpp
       |
       v
object files (.o)
       |
       v
link_elf + linker script + libraries
       |
       v
ELF firmware (.elf)
       |
       +--> inspect_elf_header / sections / segments / symbols
       +--> inspect_memory_usage / disassembly
       |
       +--> elf_to_bin  -> .bin
       +--> elf_to_hex  -> .hex
```

## 6. Result semantics

The build and conversion wrappers return a dictionary with fields such as:
- `success`: whether the executable returned exit code zero.
- `tool`: logical tool name.
- `output`: output path (and `input`/`format` where relevant).
- `returncode`: process exit code.
- `stdout`: captured standard output.
- `stderr`: captured standard error.

Inspection wrappers generally return `output` rather than `stdout`. Output is truncated to a bounded size by the Python wrapper. A `success` result means the command completed successfully; it does not independently validate the firmware's hardware behavior.

## 7. Tool execution and safety

- The execution layer accepts a registered logical tool name and a sequence of individual arguments.
- It invokes subprocesses without a shell (`shell=False`).
- Non-zero exit codes are returned as failures; they must not be treated as success.
- Do not pass a single shell command string to the low-level runner.
- Validate user-provided file paths and target settings before invoking tools.
- Do not run a flash/program operation as a side effect of a compile or conversion request.

## 8. Cross-platform packaging

The intended EmbiMind distribution keeps Python modules and MCP tool definitions identical across Windows and Linux. Only the platform-specific contents of `toolchain/` are replaced.

The agreed executable-resolution order is:
1. Environment-variable override.
2. Bundled executable under `toolchain/`.
3. System `PATH`.

The resolver must map logical names to the correct host executable filename and must not expose platform-specific filenames in MCP tool arguments. This lookup policy is an architectural requirement; verify the implementation before relying on it in a release.

## 9. Related OpenOCD documentation

The supplied OpenOCD User's Guide is release 0.12.0 (20 December 2022). It covers adapter hardware, interface/board/target configuration, reset configuration, flash programming, GDB integration, and OpenOCD commands. Keep OpenOCD-specific command syntax and target configuration in the OpenOCD reference/catalogue, not in this ARM GNU toolchain catalogue.
