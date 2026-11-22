# OpenOCD Comprehensive System & Architecture Guide
**Open On-Chip Debugger (Release 0.12.0)**  
*An Exhaustive, Structured, AI-Understandable & Machine-Parseable Knowledge Base*

---

## Table of Contents
1. [Executive Overview & Foundational Principles](#1-executive-overview--foundational-principles)
   - 1.1 What is OpenOCD?
   - 1.2 Core Mission & Capabilities
   - 1.3 Client-Server Architecture & Communication Channels
   - 1.4 The Two Execution Stages: Configuration Stage vs. Run Stage
2. [Debug Adapter & Hardware Interfacing](#2-debug-adapter--hardware-interfacing)
   - 2.1 Hardware Interface Dongles & Selection Criteria
   - 2.2 Adapter Families & Controller Architectures
   - 2.3 Physical Signaling, Voltage Levels, and Cabling
   - 2.4 Adaptive Clocking (RTCK) vs. Fixed Clocking
3. [Transport Layer Mechanics](#3-transport-layer-mechanics)
   - 3.1 JTAG (IEEE 1149.1 / IEEE 1149.7)
   - 3.2 SWD (Serial Wire Debug) & SWD Multi-Drop (SW-DP/SWJ-DP v2)
   - 3.3 SWIM (Single Wire Interface Module for STM8)
   - 3.4 SPI Transport
4. [JTAG Scan Chains, TAPs, and ARM DAPs](#4-jtag-scan-chains-taps-and-arm-daps)
   - 4.1 Test Access Port (TAP) Fundamentals & State Machine
   - 4.2 TAP Declaration, Scan Chain Order, and Naming Conventions
   - 4.3 Autoprobing & Blind Interrogation
   - 4.4 Dynamic Scan Chains & JTAG Route Controllers (JRC / ICEPick)
   - 4.5 ARM Debug Access Port (DAP) Architecture (ADIv5 & ADIv6)
5. [Target (CPU) Configuration & Execution Models](#5-target-cpu-configuration--execution-models)
   - 5.1 Supported CPU Architectures and Cores
   - 5.2 Target Creation, Dotted Names, and Target Object Commands
   - 5.3 Work Areas (SRAM Allocation, Backup, and MMU Interaction)
   - 5.4 Symmetric Multiprocessing (SMP) and Multicore Operation
   - 5.5 Target States, Run Control, Registers, and Memory Access
6. [Reset Configuration & Control Strategies](#6-reset-configuration--control-strategies)
   - 6.1 Reset Signal Taxonomy: SRST vs. TRST vs. Emulation vs. Watchdog
   - 6.2 Hardware Constraints, Signal Combinations, and Drive Modes
   - 6.3 Reset Gating and Connect Timing
   - 6.4 Reset Event Lifecycle & Custom Reset Handling Sequences
7. [The Event-Driven Automation Engine](#7-the-event-driven-automation-engine)
   - 7.1 TAP Events vs. Target Events
   - 7.2 Event Flow Triggers: Reset Sequence, GDB Lifecycle, and Examine Phases
   - 7.3 Asynchronous Event Polling & State Change Propagation
8. [Flash Subsystem & In-System Programming](#8-flash-subsystem--in-system-programming)
   - 8.1 Memory-Mapped NOR Flash (CFI, Microcontroller Internals)
   - 8.2 Serial Flash Interfaces (SPI, QuadSPI, OctoSPI, SPIFI, SMI, JTAGSPI)
   - 8.3 NAND Flash Subsystem (Pages, Blocks, OOB, Hardware/Software ECC, Bad Block Markers)
   - 8.4 Safe Flash Programming Workflow & Automated Recovery
9. [PLD / FPGA In-System Configuration](#9-pld--fpga-in-system-configuration)
   - 9.1 Boundary Scan Infrastructure & Device Loading
   - 9.2 Xilinx Virtex/Spartan/Zynq Bitstream Flow (IEEE 1532 ISC)
10. [Debug Interfaces, GDB Integration, & RTOS Awareness](#10-debug-interfaces-gdb-integration--rtos-awareness)
    - 10.1 Remote GDB Protocol Integration (TCP Socket & Stdin/Stdout Pipes)
    - 10.2 Memory Map Publication & Flash Programming via vFlash
    - 10.3 Non-Intrusive Memory Inspection (Live Background Inspection)
    - 10.4 Multithreaded RTOS Support & Symbol Extraction
    - 10.5 Hardware Threads (`hwthread`) in SMP Architectures
11. [Hardware Tracing, Real-Time Transfer (RTT), & Telemetry](#11-hardware-tracing-real-time-transfer-rtt--telemetry)
    - 11.1 ARM Embedded Trace Macrocell (ETM) & Trace Port Drivers
    - 11.2 CoreSight TPIU, SWO, SWV, and ITM Stimulus
    - 11.3 CoreSight Cross-Trigger Interface (CTI) & Trigger Matrix (CTM)
    - 11.4 SEGGER Real Time Transfer (RTT) Implementation
    - 11.5 Software Tracing via DCC (Debug Communications Channel) & libdcc
12. [Boundary Scan & Hardware Testing](#12-boundary-scan--hardware-testing)
    - 12.1 Serial Vector Format (SVF)
    - 12.2 Xilinx Serial Vector Format (XSVF)
    - 12.3 IPDBG JTAG-Host Server
13. [Configuration File Hierarchy & Project Organization](#13-configuration-file-hierarchy--project-organization)
    - 13.1 Directory Conventions: `interface/`, `target/`, `board/`, and User Configurations
    - 13.2 Variable Naming Guidelines and Cross-Script Communication
    - 13.3 Structured Execution: `init_targets` and `init_board` Procedures
    - 13.4 Translating Proprietary Debugger Scripts (Lauterbach, BDI, CCS)
14. [The Jim-Tcl Scripting Engine & RPC Server](#14-the-jim-tcl-scripting-engine--rpc-server)
    - 14.1 Jim-Tcl Core Philosophy: Strings, Quoting, and Non-Existent Control Flow
    - 14.2 Variable Scoping, Dynamic Command Creation, and Macro Constructs
    - 14.3 Headless Machine Interface: The Tcl RPC Protocol & Async Notifications
15. [Operational Playbook & Troubleshooting Encyclopedia (FAQ)](#15-operational-playbook--troubleshooting-encyclopedia-faq)
    - 15.1 Clock Synchronization & Adaptive Clocking Nuances
    - 15.2 Handling Low-Power States, Sleep Modes, and `WFI` Instruction Pitfalls
    - 15.3 Watchdog Management During Halt-Mode Debugging
    - 15.4 GDB Stack Frame Climbing and Non-Fatal Data Aborts
    - 15.5 Broken Reset Layouts & JTAG Scan Chain Failures

---

## 1. Executive Overview & Foundational Principles

### 1.1 What is OpenOCD?
The **Open On-Chip Debugger (OpenOCD)** is an open-source, vendor-independent software suite that provides in-system programming, advanced run-control hardware debugging, and boundary-scan hardware testing for embedded target microcontrollers, digital signal processors (DSPs), systems-on-chip (SoCs), and programmable logic devices (FPGAs/CPLDs).

Originally created in 2005 by Dominic Rath at the University of Applied Sciences Augsburg, OpenOCD has expanded into the industry-standard bridge connecting development hosts running host-side debuggers (such as the GNU Project Debugger, GDB) or flash programming scripts to target hardware via physical debug adapters.

### 1.2 Core Mission & Capabilities
1. **Target Control (Halt-Mode Debugging)**: Direct control over CPU cores—halting, stepping, single instruction execution, software/hardware breakpoints, data watchpoints, vector catching, and complete architectural register access.
2. **Flash Memory Subsystem**: Programming, erasing, verification, lock/unlock management, and sector protection for internal microcontroller flash (e.g., STM32, NXP LPC, Atmel SAM, TI MSP432/Stellaris, Nordic nRF5x, Cypress PSoC), external CFI-compliant NOR flash, SPI/QSPI/OctoSPI memories, and raw NAND flashes (with software and hardware ECC engines).
3. **Multi-Transport Interfacing**: Native handling of standard JTAG (IEEE 1149.1 / IEEE 1149.7), ARM Serial Wire Debug (SWD), STMicroelectronics SWIM, and serial SPI bitbang/transports.
4. **Boundary Scan & Board-Level Verification**: Execution of Serial Vector Format (SVF) and Xilinx Serial Vector Format (XSVF) files to verify circuit assembly, pin connections, solder bridges, and program logic devices.
5. **Real-Time Telemetry & Hardware Tracing**: Instruction and data trace extraction via ARM Embedded Trace Macrocell (ETM), CoreSight Trace Port Interface Unit (TPIU), Serial Wire Output (SWO/SWV), Instrumentation Trace Macrocell (ITM), and SEGGER Real Time Transfer (RTT).
6. **Operating System & Thread Awareness**: Automatic thread-state reconstruction for RTOS environments (FreeRTOS, Zephyr, ThreadX, NuttX, ChibiOS, embKernel, mqx, uC/OS-III, RIOT, Linux kernel) and symmetric multiprocessing (SMP) hardware thread presentation.

### 1.3 Client-Server Architecture & Communication Channels
OpenOCD operates as an asynchronous background daemon listening on configurable network ports or local pipe descriptors:
- **GDB Server (`gdb_port`, default: `3333`)**: Implements the GDB Remote Serial Protocol (RSP). GDB instances connect via `target extended-remote localhost:3333` to control targets, examine memory maps, transparently trigger flash programming (`vFlash`), and debug source code. In multicore setups, additional targets listen on sequential ports (`3334`, `3335`, etc.).
- **Telnet Interactive Shell (`telnet_port`, default: `4444`)**: Interactive text-based console designed for human interaction. Accepts full Jim-Tcl commands, diagnostic primitives, and direct target control commands. Commands can also be executed from inside GDB using `monitor <command>`.
- **Tcl Machine Interface (`tcl_port`, default: `6666`)**: A headless RPC interface designed for IDEs, continuous integration (CI) runners, and automated test harnesses. Commands are passed as UTF-8/ASCII strings terminated by byte `0x1a` (`Ctrl-Z`), and replies (including structured associative arrays for asynchronous target events) are terminated by `0x1a`.
- **Stdio Pipe Interface (`-pipe` / `gdb_port pipe`)**: Direct bi-directional pipe mode enabling a parent GDB process to spawn OpenOCD locally as a child process without opening network sockets.

```
       +-------------------------------------------------------+
       |               Host Software Layer                     |
       |  +------------------+  +-------------+  +-----------+ |
       |  | GDB Client / IDE |  | Telnet User |  | CI Script | |
       |  +--------+---------+  +------+------+  +-----+-----+ |
       +-----------|-------------------|---------------|-------+
                   | (Port 3333)       | (Port 4444)   | (Port 6666)
       +-----------v-------------------v---------------v-------+
       |                  OpenOCD Core Daemon                  |
       |  +-------------------------------------------------+  |
       |  |           Jim-Tcl Execution Engine              |  |
       |  +-------------------------------------------------+  |
       |  | Core Server (Run Control, Event Polling, RTOS)  |  |
       |  +-------------------------------------------------+  |
       |  | Drivers: Flash (NOR/NAND/SPI) | FPGA/PLD | Trace|  |
       |  +-------------------------------------------------+  |
       |  | Transport Engine: JTAG Scan Chain / SWD / SWIM  |  |
       |  +-------------------------------------------------+  |
       |  | Hardware Adapter Driver Layer (FTDI, CMSIS-DAP) |  |
       +-----------------------+-------------------------------+
                               | USB / Parallel / Ethernet / PCIe
       +-----------------------v-------------------------------+
       |             Hardware Debug Probe (Dongle)             |
       |            (e.g., ST-Link, J-Link, FT2232H)           |
       +-----------------------+-------------------------------+
                               | Electrical Interface (JTAG / SWD)
       +-----------------------v-------------------------------+
       |                 Target Embedded System                |
       |       +----------+   +----------+   +----------+      |
       |       | TAP / DAP|-->| CPU Core |-->| Flash/RAM|      |
       |       +----------+   +----------+   +----------+      |
       +-------------------------------------------------------+
```

### 1.4 The Two Execution Stages: Configuration Stage vs. Run Stage
OpenOCD processes scripts and state transitions using two discrete operational phases:
1. **Configuration Stage (`config` mode)**:
   - Entered when the OpenOCD process starts.
   - Used to define system architecture: adapter selection (`adapter driver`), transport protocols (`transport select`), JTAG scan chain TAPs (`jtag newtap`), ARM DAPs (`dap create`), CPU debug targets (`target create`), reset configurations (`reset_config`), flash banks (`flash bank`), and network bindings.
   - Target registers and device memories *cannot* be accessed during this stage because hardware communication links have not yet been validated.
2. **Run Stage (`exec` mode)**:
   - Triggered either explicitly by invoking the `init` command or implicitly at the end of configuration script evaluation.
   - OpenOCD executes `jtag_init` (or equivalent transport init), resets and inspects the physical scan chain, verifies expected IDCODEs, executes `init_targets` and `init_board` procedures, starts TCP server listeners, and opens client ports.
   - Run control (`halt`, `resume`, `step`), memory operations (`mdw`, `mww`), image downloads (`load_image`), and flash programming commands become fully operational.

---

## 2. Debug Adapter & Hardware Interfacing

### 2.1 Hardware Interface Dongles & Selection Criteria
OpenOCD acts as host-side software communicating through an external hardware module called a **debug adapter** (or dongle). Adapters translate host communication (USB bulk/HID packets, Ethernet TCP/IP, or parallel port I/O) into the physical electrical signals required by the target.

When selecting an adapter, key constraints include:
1. **Supported Transports**: Does the hardware implement multi-wire JTAG, two-wire ARM SWD, or STM8 SWIM?
2. **I/O Logic Voltage**: Does the adapter feature active bidirectional level shifters supporting target voltages from 1.2V, 1.8V, 2.8V, 3.3V, up to 5V? Direct connection of 3.3V-only adapters to 1.8V chips risks silicon destruction.
3. **Signal Pinout & Connectors**: Standard 20-pin ARM IDC, 10-pin Cortex Debug (0.05" pitch), 14-pin TI, 14-pin Altera, or flexible flying leads ("octopus" cables).
4. **Adaptive Clocking (RTCK)**: Capability to receive return-clock feedback from synthesizable cores running variable or gated internal clocks.

### 2.2 Adapter Families & Controller Architectures
- **FTDI Multi-Protocol Synchronous Serial Engine (MPSSE) Chips**:
  - `FT2232D` (USB Full-Speed 12 Mbps), `FT2232H` / `FT4232H` (USB High-Speed 480 Mbps), and `FT232H` (Single-channel High-Speed).
  - OpenOCD's `ftdi` driver directly communicates with libusb-1.0 in asynchronous mode, bypassing wrapper libraries. Supports bitmasked pin definitions for arbitrary buffers (push-pull, open-drain, tristate).
- **FTDI UART Bridge Bitbang (`ft232r`)**:
  - Reuses modem control lines (TXD, RXD, RTS, CTS, DTR, DCD) on standard FT232R/FT230X/FT231X UART converters to bitbang JTAG lines.
- **ARM CMSIS-DAP Compliant Probes**:
  - Open standard developed by ARM. Available as CMSIS-DAP v1 (USB HID based, driverless on most OSes) and CMSIS-DAP v2 (USB Bulk endpoints for high throughput). Supports multi-drop SWD.
- **SEGGER J-Link Family**:
  - High-performance microcontroller-based probes (AT91SAM7 or STM32-based). Capable of hardware-managed JTAG, SWD, and adaptive clocking. Includes custom memory inspection and EMUCOM communication channels.
- **STMicroelectronics ST-LINK (v1, v2, v3)**:
  - Bundled on Discovery and Nucleo development boards.
  - *High-Level Adapter (`hla` driver)*: Treats ST-LINK as an intelligent controller where low-level JTAG/SWD transactions are abstracted inside ST firmware.
  - *Native Direct DAP Driver (`st-link` driver)*: Communicates directly with ARM ADIv5 DAP via firmware extension commands (from ST-Link/V2 firmware V2J24 and STLINK-V3), enabling multi-AP access.
- **Microcontroller Bitbanging & GPIO**:
  - Native Linux direct memory-mapped GPIO access for embedded single-board computers (BCM2835 on Raspberry Pi, AM335x on BeagleBone, NXP i.MX).
  - Linux `libgpiod` driver (modern userspace GPIO character device API) and legacy `sysfsgpio`.
- **Virtual / Emulation Adapters**:
  - `vdebug`: Connects OpenOCD to Cadence virtual debug server running RTL simulations.
  - `jtag_dpi`: SystemVerilog Direct Programming Interface for hardware emulation environments.
  - `remote_bitbang`: Sends ASCII-encoded bit transitions over TCP/Unix sockets to external simulators.
  - `xlnx_pcie_xvc`: Xilinx Virtual Cable over PCI Express configuration space registers.

### 2.3 Physical Signaling, Voltage Levels, and Cabling
JTAG requires a shared ground and dedicated lines:
- **TCK (Test Clock)**: Driven by the adapter.
- **TMS (Test Mode Select)**: Sampled on the rising edge of TCK to step through the TAP state machine.
- **TDI (Test Data In)**: Serial data shifted into instruction or data registers.
- **TDO (Test Data Out)**: Serial data shifted out of registers, sampled on the falling edge of TCK.
- **nTRST (Test Reset)**: Optional asynchronous reset of the TAP controller state machine.
- **nSRST (System Reset)**: Active-low line resetting board-level hardware, processors, and peripherals.

### 2.4 Adaptive Clocking (RTCK) vs. Fixed Clocking
In synthesized digital designs (especially ARM7TDMI and ARM9 cores), the JTAG test clock (TCK) is asynchronous to the internal system CPU core clock. To capture JTAG signals reliably, the core synchronizes TCK using internal flip-flops:
1. **The Clock Ratio Constraint**: The maximum JTAG clock must not exceed **1/6th** of the CPU clock frequency (or **1/8th** for ARM11 cores). If a core boots at a slow 32 kHz real-time clock frequency before enabling a 400 MHz PLL, a JTAG clock faster than ~5 kHz will cause lost bits and communication failure.
2. **Adaptive Clocking (RTCK)**: The target outputs an `RTCK` ("Return TCK") signal. The adapter asserts TCK, waits until the target acknowledges synchronization by asserting RTCK, and only then samples TDO. This automatically adjusts JTAG speed to match whatever CPU frequency is active—including across low-power sleep modes.
3. **Fixed Fallback**: If hardware does not support RTCK, scripts must initialize the scan chain at a safe low frequency (e.g., `adapter speed 100` for 100 kHz) during reset, and ramp up to full speed (e.g., `adapter speed 10000`) inside the `reset-init` handler once PLLs are locked.

---

## 3. Transport Layer Mechanics

```
                         Supported Transports
    +--------------------------------------------------------------+
    |                                                              |
    |  +------------+   +------------+   +------------+   +-----+  |
    |  |    JTAG    |   |    SWD     |   |    SWIM    |   | SPI |  |
    |  | (Multi-TAP |   | (2-Wire    |   | (STM8 Only |   |     |  |
    |  | Boundary)  |   | Multi-drop)|   | Single-pin)|   |     |  |
    |  +------------+   +------------+   +------------+   +-----+  |
    +--------------------------------------------------------------+
```

### 3.1 JTAG (IEEE 1149.1 / IEEE 1149.7)
JTAG daisy-chains multiple TAPs across a board or inside a single silicon package. A single adapter drives TDI into TAP #0, whose TDO feeds TAP #1, until the final TDO returns to the adapter. All TAPs concurrently observe TCK and TMS. JTAG provides non-intrusive boundary scan testing, instruction execution, and register inspection.

### 3.2 SWD (Serial Wire Debug) & SWD Multi-Drop
Developed by ARM as a low pin-count alternative to JTAG:
- Utilizes only two bidirectional physical lines: **SWCLK** (clock driven by host) and **SWDIO** (bidirectional serial data with half-cycle turn-around).
- **No Boundary Scan**: SWD is strictly a debug/programming protocol interfacing directly to an ARM Debug Access Port (DAP).
- **SWD Multi-Drop (SW-DP v2 / SWJ-DP v2)**: Allows connecting up to 32 target devices to a single SWD adapter bus. Each target is addressed via a unique 28-bit target ID (`-dp-id`) and an optional 4-bit instance identifier (`-instance-id`), selected by writing to the DP `TARGETSEL` register during bus enumeration. Supported by `cmsis-dap` (v2.0), `ftdi`, and bitbang drivers.

### 3.3 SWIM (Single Wire Interface Module)
A proprietary STMicroelectronics low-pin count debug transport engineered for the 8-bit STM8 family. Operates over a single open-drain bi-directional wire. SWIM does not implement standard scan chains; OpenOCD models it logically using a virtual TAP (`swim newtap`).

### 3.4 SPI Transport
Four-wire synchronous interface used for direct in-system programming of external flash chips connected to microcontrollers or FPGAs.

---

## 4. JTAG Scan Chains, TAPs, and ARM DAPs

### 4.1 Test Access Port (TAP) Fundamentals & State Machine
Every JTAG device houses a 16-state finite state machine (FSM) transitioned via TMS transitions on the rising edge of TCK:

```
                           +--------------+
                           | Test-Logic-  |
             +------------>|    Reset     |<------------+
             |             +-------+------+             |
             |                     |                    |
             |             +-------v------+             |
             |             |  Run-Test /  |             |
             |             |     Idle     |             |
             |             +-------+------+             |
             |                     |                    |
             |      +--------------+--------------+     |
             |      |                             |     |
             | +----v----+                   +----v----+|
             | | Select- |                   | Select- ||
             | | DR-Scan |                   | IR-Scan ||
             | +----+----+                   +----+----+|
             |      |                             |     |
             | +----v----+                   +----v----+|
             | | Capture |                   | Capture ||
             | |   DR    |                   |   IR    ||
             | +----+----+                   +----+----+|
             |      |                             |     |
             | +----v----+                   +----v----+|
             | | Shift-DR| (Shifts Data)     | Shift-IR| (Shifts Opcode)
             | +----+----+                   +----+----+|
             |      |                             |     |
             | +----v----+                   +----v----+|
             | | Exit1-DR|                   | Exit1-IR||
             | +----+----+                   +----+----+|
             |      |                             |     |
             | +----v----+                   +----v----+|
             | | Pause-DR|                   | Pause-IR||
             | +----+----+                   +----+----+|
             |      |                             |     |
             | +----v----+                   +----v----+|
             | | Update- |                   | Update- ||
             | |   DR    |                   |   IR    ||
             | +----+----+                   +----+----+|
             +------+-----------------------------+-----+
```

- **Instruction Register (IR)**: Selects active internal registers. Has a fixed bit length (`-irlen`).
- **Data Registers (DR)**: Variable length depending on active instruction. Common DRs include `IDCODE` (32-bit chip ID), `BYPASS` (1-bit shift register), and proprietary core scan registers (e.g., EmbeddedICE or RISC-V DTM).

### 4.2 TAP Declaration, Scan Chain Order, and Naming Conventions
TAPs are declared using `jtag newtap <chipname> <tapname> [options]`.
- **Dotted Name**: Concatenation of `<chipname>.<tapname>` (e.g., `stm32f1x.cpu`, `omap3530.jrc`).
- **Declaration Order Rule**: Must strictly mirror physical layout from TDI to TDO. The device closest to the adapter's TDI pin is declared first; the device connected directly to the adapter's TDO pin is declared last.

### 4.3 Autoprobing & Blind Interrogation
When a board's TAPs are unknown, OpenOCD can reset the JTAG bus and shift through the data register to identify `IDCODE` registers:
- TAPs supporting `IDCODE` capture a 32-bit code starting with a logical `1` at bit 0.
- TAPs lacking `IDCODE` default to the 1-bit `BYPASS` register (returning `0`).
- OpenOCD automatically isolates individual 32-bit IDCODEs and outputs template `jtag newtap` configurations including manufacturer IDs, part numbers, and silicon versions.

### 4.4 Dynamic Scan Chains & JTAG Route Controllers (JRC / ICEPick)
Complex multi-core SoCs (e.g., TI OMAP, DaVinci) house power-saving JTAG Route Controllers (e.g., ICEPick). At power-on, secondary cores (DSP, GPU, secondary ARM cores) are electrically disconnected from the scan chain to save power and keep instruction shifting fast.
OpenOCD configures event handlers (`tap-enable`, `tap-disable`) on the JRC TAP to dynamically inject special JTAG instruction sequences that link or unlink slave TAPs during execution.

### 4.5 ARM Debug Access Port (DAP) Architecture (ADIv5 & ADIv6)
Modern ARM cores (ARMv6-M, ARMv7, ARMv8) separate the physical debug port from memory and core registers via the ARM Debug Interface (ADI):
- **Debug Port (DP)**: Physical interface (SW-DP for Serial Wire, JTAG-DP for JTAG). Handles powering up debug domains (`CDBGPWRUPREQ`, `CSYSPWRUPREQ`).
- **Access Ports (AP)**: Internal buses connected to DP.
  - `MEM-AP`: Memory Access Port that acts as an AHB/AXI master, granting direct bus access to target physical SRAM, flash, and memory-mapped peripheral registers without halting the CPU.
  - `JTAG-AP`: Bridges out to legacy core scan chains.
- **ADIv5 vs. ADIv6**:
  - *ADIv5*: Uses 8-bit numeric AP indexes (AP #0, AP #1).
  - *ADIv6*: Fully hierarchical bus memory map where APs are identified by 64-bit base addresses in a CoreSight ROM Table.
- **DAP Creation**: Desde version 0.11.0, DAPs are explicitly instantiated via `dap create <dap_name> -chain-position <dotted.name>` before creating CPU targets.

---

## 5. Target (CPU) Configuration & Execution Models

### 5.1 Supported CPU Architectures and Cores
OpenOCD implements core execution control modules across major processor families:
- **ARM Architectures**:
  - ARMv4/ARMv5: `arm7tdmi`, `arm720t`, `arm9tdmi`, `arm920t`, `arm926ejs`, `arm946e`, `arm966e`, `feroceon`, `dragonite`, `xscale`.
  - ARMv6: `arm11`.
  - ARMv7-A / ARMv8-A: `cortex_a`, `aarch64`.
  - ARMv7-R: `cortex_r4`.
  - ARMv6-M / ARMv7-M / ARMv8-M: `cortex_m` (Microcontrollers: M0, M0+, M1, M3, M4, M7, M23, M33).
  - ARM Debug Access Bus Master: `mem_ap` (CPU-less direct bus master).
- **RISC-V**: RV32 and RV64 targets complying with Debug Specifications 0.11 and 0.13, supporting hardware threads (harts), Program Buffers (`progbuf`), System Bus Access (`sysbus`), and abstract commands.
- **Xtensa**: Cadence/Tensilica Xtensa LX6, LX7, NX cores, and Espressif ESP32, ESP32-S2, ESP32-S3 SoCs with configurable windowed registers and SMP break networks.
- **MIPS**: `mips_m4k`, `mips_mips64`.
- **Other Architectures**: Synopsys ARC (`arc_em`), OpenRISC 1000 (`or1k`), Intel Quark IA-32 (`quark_x10xx`, `quark_d20xx`), STMicroelectronics `stm8`, EnSilica `esirisc`.

### 5.2 Target Creation, Dotted Names, and Target Object Commands
Targets are instantiated using:
```tcl
target create <target_name> <type> -dap <dap_name> [options]
# Or for non-ADIv5 targets:
target create <target_name> <type> -chain-position <dotted.name> [options]
```
Upon creation, `<target_name>` is registered as a first-class Jim-Tcl command object. Invoking `$target_name <subcommand>` directly controls that specific target (e.g., `$target_name arp_halt`, `$target_name mdw <addr>`).

### 5.3 Work Areas (SRAM Allocation, Backup, and MMU Interaction)
A **Work Area** is a reserved pool of on-chip target RAM assigned to OpenOCD via `-work-area-phys <addr> -work-area-size <bytes>`:
- **Acceleration**: Allows OpenOCD to download small binary helper algorithms ("flash loaders") directly into target SRAM. The target CPU then executes this loader at full clock speed to write incoming bulk flash packets, multiplying programming throughput by up to 50x compared to stepping over raw JTAG.
- **Backup Strategy**: `-work-area-backup 0` assumes OpenOCD owns the memory (typical during flash programming). Setting it to `1` forces OpenOCD to read out the original SRAM content before executing algorithms and restore it afterward (critical when attaching to running production systems).
- **MMU Interaction**: On processors with virtual memory enabled (ARMv7-A, AArch64, MIPS), virtual addresses must be specified via `-work-area-virt`.

### 5.4 Symmetric Multiprocessing (SMP) and Multicore Operation
For multi-core systems sharing a cache-coherent memory map:
1. Targets are instantiated individually for each core with corresponding core IDs (`-coreid 0`, `-coreid 1`).
2. Targets are linked into an SMP group via `target smp <target1> <target2>`.
3. **Synchronized Run Control**:
   - Setting a hardware breakpoint on one target sets identical breakpoints on all SMP cores.
   - Halting or resuming one core automatically halts or resumes all sibling cores.
   - When a breakpoint is hit, OpenOCD switches GDB context to the specific core that triggered the halt.

### 5.5 Target States, Run Control, Registers, and Memory Access
- **Target States**: `unknown`, `running`, `halted`, `reset`, `debug-running`.
- **Run Control**: `halt` requests asynchronous core suspension; `resume [address]` releases the core to execute; `step [address]` single-steps one assembly instruction.
- **Memory Access Modes**: Accesses are sized strictly as 8-bit bytes (`mdb`), 16-bit halfwords (`mdh`), 32-bit words (`mdw`), or 64-bit doublewords (`mdd`). Memory-mapped I/O peripherals require strict adherence to their native register widths.

---

## 6. Reset Configuration & Control Strategies

### 6.1 Reset Signal Taxonomy: SRST vs. TRST vs. Emulation vs. Watchdog
Reset is one of the most error-prone areas in JTAG debugging due to electrical and architectural subtleties:
1. **System Reset (SRST)**: Physical active-low wire (`nSRST`) resetting the entire board, including peripherals, buses, and CPU cores. Equivalent to pressing a physical reset button.
2. **Test Reset (TRST)**: Physical active-low wire (`nTRST`) resetting only the JTAG TAP state machine into `Test-Logic-Reset`. Does not affect CPU or peripheral state.
3. **Emulation / Soft Reset**: Software-driven reset executed over debug instructions without asserting physical pins (e.g., writing ARM Cortex-M `AIRCR.SYSRESETREQ` or `AIRCR.VECTRESET`).
4. **Watchdog / Core Reset**: Reset initiated by on-chip watchdog counters or internal system controllers.

### 6.2 Hardware Constraints, Signal Combinations, and Drive Modes
Reset capabilities are defined via `reset_config`:
- **Available Signals**: `none`, `trst_only`, `srst_only`, `trst_and_srst`.
- **Signal Coupling Faults**:
  - `separate`: SRST and TRST operate independently.
  - `srst_pulls_trst`: Asserting system reset inadvertently pulls down TRST (e.g., NXP LPC2000 hardware bug), resetting the debug connection.
  - `trst_pulls_srst`: Asserting TRST resets the entire system.
  - `combined`: Both lines are tied together.
- **Electrical Drive Types**:
  - `srst_open_drain` vs. `srst_push_pull`.
  - `trst_open_drain` vs. `trst_push_pull`.
  Most boards use open-drain outputs with pull-up resistors to allow multiple reset sources.

### 6.3 Reset Gating and Connect Timing
- **Clock Gating**: `srst_gates_jtag` indicates that while SRST is held low, the target gates off the JTAG clock (TDO freezes). OpenOCD must not attempt JTAG operations while reset is asserted. The converse is `srst_nogate`.
- **Under-Reset Connection (`connect_assert_srst`)**: OpenOCD asserts SRST *before* initiating JTAG/SWD communication. Indispensable for recovering "bricked" microcontrollers whose flash firmware immediately reconfigures debug pins as GPIO or enters unclocked low-power sleep upon boot.

### 6.4 Reset Event Lifecycle & Custom Reset Handling Sequences
Standard reset types:
- `reset run`: Asserts reset, releases it, and allows the target to run freely.
- `reset halt`: Asserts reset, halts the core at the very first instruction (reset vector), and transfers control to the debugger before application code executes.
- `reset init`: Halts the target at reset vector, then executes the target's board-specific `reset-init` script to initialize clocks, PLLs, SDRAM, and peripheral routing.

```
       +-------------------------------------------------------+
       |                  reset init Lifecycle                 |
       +-------------------------------------------------------+
                                   |
                         [reset-start event]
                                   |
                      Assert SRST / TRST signals
                                   |
                      [reset-assert-pre event]
                                   |
                        Trigger Target Reset
                                   |
                     [reset-assert-post event]
                                   |
                     [reset-deassert-pre event]
                                   |
                     Deassert Reset (Release SRST)
                                   |
                    [reset-deassert-post event]
                                   |
                          Halt Target Core
                                   |
                          [reset-end event]
                                   |
                         [reset-init event]
                    (Executes PLL & SDRAM Init)
                                   |
                         Target Ready for Debug
```

---

## 7. The Event-Driven Automation Engine

### 7.1 TAP Events vs. Target Events
OpenOCD features a bidirectional asynchronous event notification framework:
- **TAP Events**: Attached to JTAG TAPs via `jtag configure <tap> -event <event_name> <body>`. Governs scan chain maintenance: `post-reset`, `setup`, `tap-enable`, `tap-disable`.
- **Target Events**: Attached to CPU targets via `$target_name configure -event <event_name> <body>`. Governs debugging milestones, flash programming hooks, and run control.

### 7.2 Event Flow Triggers: Reset Sequence, GDB Lifecycle, and Examine Phases
- **Target Reset Pipeline**:
  - `reset-start`: Fires prior to asserting reset lines. Best place to drop adapter clock speed (`adapter speed 100`) in case reset clears PLL registers.
  - `reset-assert`: Custom routine to force core reset when SRST is absent.
  - `reset-deassert-post`: Core has emerged from reset.
  - `reset-init`: Main hook for board initialization (enabling external RAM, configuring PLL multipliers, increasing JTAG clock).
- **GDB Lifecycle Events**:
  - `gdb-attach`: Fires when a GDB client connects. Default behavior halts the target. Can be cleared to enable non-intrusive debugging of live processes.
  - `gdb-detach`: Fires on client disconnection.
  - `gdb-flash-erase-start` / `gdb-flash-write-end`: Pre- and post-flashing automation hooks.
- **Run Control Triggers**:
  - `debug-halted`: Target suspended on breakpoint or debug request.
  - `debug-resumed`: Target resumed normal execution.
  - `step-start` / `step-end`: Single-step cycle boundaries.

### 7.3 Asynchronous Event Polling & State Change Propagation
Target hardware runs asynchronously to the host. OpenOCD executes a background event poller (`poll on`, default 100 ms interval) that queries target registers via JTAG/SWD:
- Detects spontaneous core halts (breakpoints, hard faults, watchpoints).
- Intercepts debug messages sent over JTAG DCC.
- Detects target power loss or target reset events.
- Broadcasts updates to all connected GDB, Telnet, and Tcl RPC clients.

---

## 8. Flash Subsystem & In-System Programming

### 8.1 Memory-Mapped NOR Flash (CFI, Microcontroller Internals)
NOR flash allows random byte/word read access identical to RAM, but requires high voltages or charge pumps to program bits (`1 -> 0`) and block erase operations to reset bits (`0 -> 1`):
- **Common Flash Interface (CFI)**: Universal standard (`cfi` driver) for external NOR flash chips attached to system address/data buses. Queries manufacturer geometry dynamically.
- **On-Chip Microcontroller Flash**: Integrated flash modules controlled via vendor-specific registers (e.g., STM32 Embedded Flash memory interface, Atmel SAM NVM controller, TI Stellaris/Tiva flash). Configured via `flash bank <name> <driver> <base> <size> <chip_width> <bus_width> <target>`.

### 8.2 Serial Flash Interfaces (SPI, QuadSPI, OctoSPI, SPIFI, SMI, JTAGSPI)
Modern systems frequently execute or boot from serial NOR flash over high-speed buses:
- `stmqspi`: STMicroelectronics QuadSPI and OctoSPI controllers (STM32F4, F7, L4, L4+, H7). Supports memory-mapped read mode and high-speed write access.
- `lpcspifi`: NXP LPC18xx/43xx SPI Flash Interface peripheral.
- `jtagspi`: Programs SPI flash attached to FPGAs (Xilinx Spartan/Artix) by temporarily loading a proxy bitstream into the FPGA fabric that connects JTAG pins to FPGA SPI pins.

### 8.3 NAND Flash Subsystem
Unlike NOR flash, NAND flash is high-density block/page structured and accessed via sequential command/address/data cycles:
- **Geometry**: Composed of erase blocks (e.g., 128 KB) divided into pages (e.g., 2048 bytes) plus an **Out-Of-Band (OOB)** / spare area (e.g., 64 bytes per page).
- **Error Correction Code (ECC)**: NAND gates suffer bit flips. OpenOCD supports raw page access (`oob_raw`), uncorrected data (`no_oob`), software ECC computation (`oob_softecc`), and hardware ECC engine integration (`hwecc1`, `hwecc4`).
- **Bad Block Markers**: Factory bad blocks must never be erased. OpenOCD preserves markers during partition operations.

### 8.4 Safe Flash Programming Workflow & Automated Recovery
The canonical automated programming workflow in OpenOCD:
```bash
openocd -f interface/stlink.cfg -f target/stm32f4x.cfg \
  -c "program application.elf verify reset exit"
```
Under the hood, the Jim-Tcl `program` helper script executes:
1. `init`: Transitions OpenOCD into the run stage.
2. `reset init`: Halts the target at reset vector and executes PLL initialization to ensure maximum flashing speed.
3. `flash write_image erase <filename>`: Erases only the sectors mapped to loadable ELF sections, unprotects flash if requested, and writes binary data using working-area loader algorithms.
4. `verify_image <filename>`: Performs hardware CRC32 or byte-by-byte memory verification against the original binary.
5. `reset run`: Resets the target and releases it to execute application firmware.
6. `exit`: Gracefully shuts down OpenOCD.

---

## 9. PLD / FPGA In-System Configuration

OpenOCD treats Programmable Logic Devices (PLDs) and FPGAs as configurable hardware nodes on the JTAG scan chain:
- **Device Management**: Declared via `pld device <driver> <tap_name>`.
- **Bitstream Loading**: `pld load <num> <filename>` streams raw bitstream binaries directly into the FPGA's configuration memory.
- **Xilinx Virtex/Spartan/Series7 Support (`virtex2` driver)**: Fully implements IEEE 1532 In-System Configuration (ISC). Provides control over the `JSTART` instruction to initiate internal startup sequences without resetting surrounding board circuitry.

---

## 10. Debug Interfaces, GDB Integration, & RTOS Awareness

### 10.1 Remote GDB Protocol Integration
OpenOCD functions as an embedded GDB Server. It accepts standard GDB RSP packets over TCP port 3333 or stdio pipes:
```bash
# Connecting from GDB
arm-none-eabi-gdb application.elf
(gdb) target extended-remote localhost:3333
(gdb) monitor reset halt
(gdb) load
(gdb) b main
(gdb) continue
```
The `extended-remote` mode allows restarting targets and debugging across power cycles without disconnecting GDB.

### 10.2 Memory Map Publication & Flash Programming via vFlash
When `gdb_memory_map enable` is active, OpenOCD sends target XML memory maps to GDB upon connection:
- Informs GDB which address ranges represent RAM and which represent Flash.
- GDB automatically switches between **software breakpoints** (patching instructions in RAM with `BKPT`/`TRAP`) and **hardware breakpoints** (configuring core comparator registers in Flash).
- GDB's standard `load` command automatically triggers OpenOCD's internal flash programming algorithms via `vFlashErase`, `vFlashWrite`, and `vFlashDone` packets.

### 10.3 Non-Intrusive Memory Inspection (Live Background Inspection)
In industrial, robotics, or critical control systems, stopping the CPU halts real-time control loops and can cause hardware damage. If the target supports background memory bus mastering (e.g., ARM Cortex-M AHB-AP or Cortex-A AXI-AP):
1. Disable automatic halt on attach: `$_TARGETNAME configure -event gdb-attach {}`.
2. Disable memory map blocking: `gdb_memory_map disable` and GDB command `set mem inaccessible-by-default off`.
3. In GDB: `set remote interrupt-on-connect off` and connect via `target extended-remote localhost:3333`.
4. GDB can now read and display global variables, control structures, and memory-mapped I/O in real time while the CPU executes at full speed.

### 10.4 Multithreaded RTOS Support & Symbol Extraction
OpenOCD natively parses thread control blocks (TCBs) for popular operating systems:
- **Supported RTOSes**: FreeRTOS, Zephyr, ThreadX, RTEMS, ChibiOS, NuttX, RIOT, uC/OS-III, embKernel, MQX, and Linux.
- **Operation**: Enabled via `$_TARGETNAME configure -rtos auto` (or explicit name).
- When target halts, OpenOCD inspects RTOS internal thread lists in memory, reconstructs the call stack for each inactive thread from its saved stack frame, and exposes threads to GDB. Issuing `info threads` in GDB displays all operating system tasks.

### 10.5 Hardware Threads (`hwthread`) in SMP Architectures
OpenOCD's pseudo-RTOS module `hwthread` exposes symmetric cores in an SMP cluster as threads in GDB. A developer can switch active execution focus between core 0 and core 1 using GDB's standard `thread <id>` command.

---

## 11. Hardware Tracing, Real-Time Transfer (RTT), & Telemetry

### 11.1 ARM Embedded Trace Macrocell (ETM) & Trace Port Drivers
ARM ETM hardware records exact instruction execution history and data bus transactions non-intrusively at full core clock speed:
- **Trace Destinations**:
  - *On-chip Embedded Trace Buffer (ETB)*: Dedicated circular on-chip SRAM buffer (e.g., 4 KB) configured in the target script (`etb config`).
  - *External Trace Connector*: High-speed 38-pin Mictor connector routing trace data to external hardware analyzers.
- **Trace Filtering**: Configurable to capture only specific function ranges, data address accesses, or exception handlers (`etm tracemode`).

### 11.2 CoreSight TPIU, SWO, SWV, and ITM Stimulus
Cortex-M microcontrollers feature ARM CoreSight telemetry:
- **Instrumentation Trace Macrocell (ITM)**: Provides 32 software stimulus ports. Target firmware writes `printf` characters to port 0 (`ITM_STIM8(0) = c`), which the hardware transmits without CPU execution stalls.
- **Serial Wire Output (SWO)**: Single-pin high-speed asynchronous UART (NRZ) or Manchester output pin transmitting ITM packets, data watchpoint counters, and interrupt execution logs.
- **Trace Port Interface Unit (TPIU)**: Formats and serializes trace output for capture by debug adapters (e.g., ST-Link v3, J-Link) or logging to disk/TCP sockets (`tpiu configure`).

### 11.3 CoreSight Cross-Trigger Interface (CTI) & Trigger Matrix (CTM)
CTI connects internal hardware event signals across cores and peripherals via a common trigger matrix:
- Used on ARMv8-A (AArch64) multicore chips for synchronized run control.
- Enables events such as: "when Core 0 hits a breakpoint, simultaneously trigger an ETM trace halt and freeze Core 1."

### 11.4 SEGGER Real Time Transfer (RTT) Implementation
RTT enables bidirectional host-target communication at megabytes-per-second speeds over standard JTAG/SWD without auxiliary pins:
- Uses a control block structure in target SRAM with up/down circular ring buffers.
- OpenOCD automatically searches SRAM for the `"SEGGER RTT"` magic string (`rtt setup`).
- Each RTT channel is exposed to the host system as a dedicated TCP/IP port (`rtt server start <port> <channel>`), allowing terminal connections for logging and command inputs.

### 11.5 Software Tracing via DCC (Debug Communications Channel) & libdcc
For cores lacking SWO or RTT (older ARM7/ARM9), OpenOCD provides the DCC channel:
- Target firmware writes characters into coprocessor registers (`CP14`).
- OpenOCD background polling pulls these characters and prints them to the host console (`target_request debugmsgs enable`). Linux kernel early printk uses this via `CONFIG_DEBUG_ICEDCC`.

---

## 12. Boundary Scan & Hardware Testing

### 12.1 Serial Vector Format (SVF)
SVF is an industry-standard ASCII specification describing JTAG bus transactions (pin logic levels, instruction register shifts, data register masks, and expected outputs).
OpenOCD's `svf <filename>` command executes SVF test vectors directly, validating board assembly, continuity, and functional integrity on production lines.

### 12.2 Xilinx Serial Vector Format (XSVF)
Binary-compressed variant of SVF optimized for Xilinx CPLD and FPGA programming. Executed using `xsvf <tapname> <filename>`.

### 12.3 IPDBG JTAG-Host Server
An open framework for debugging synthesizable IP cores running inside FPGAs. OpenOCD serves as a JTAG-Host gateway, tunneling TCP socket commands from host waveform analyzers directly into FPGA internal test buses.

---

## 13. Configuration File Hierarchy & Project Organization

### 13.1 Directory Conventions
OpenOCD's configuration library (`$pkgdatadir/scripts`) is strictly modularized into three primary tiers:
1. **`interface/` (Debug Adapters)**: Defines adapter hardware driver, communication channels, VID/PID pairs, and pin routing (e.g., `interface/stlink.cfg`, `interface/ftdi/jtagkey2.cfg`).
2. **`target/` (Silicon Chips & SoCs)**: Defines silicon architecture: TAPs, DAPs, CPU cores, target types, default clock constraints, internal flash controllers, and watchdogs (e.g., `target/stm32f4x.cfg`, `target/k60.cfg`).
3. **`board/` (Circuit Boards & PWAs)**: Combines an interface and one or more target files. Configures board-specific components: crystal oscillators, reset signal wiring, external DRAM controllers, external NOR/NAND flash chips, and the `reset-init` procedure (e.g., `board/stm32f4discovery.cfg`).
4. **User Configuration (`openocd.cfg`)**: Created in the project directory to combine board/interface scripts, customize port assignments, define application work areas, and declare project-specific automation procedures.

### 13.2 Variable Naming Guidelines and Cross-Script Communication
Because Jim-Tcl lacks namespaces, OpenOCD uses rigorous global variable conventions:
- **Inputs to Target Configs**:
  - `CHIPNAME`: Identifies the chip instance (defaults to model name, e.g., `stm32f1x`). Boards override this when multiple identical chips exist on one scan chain.
  - `CPUTAPID`: Expected 32-bit JTAG IDCODE for CPU verification.
  - `ENDIAN`: CPU byte order (`little` or `big`).
- **Outputs from Target Configs**:
  - `_TARGETNAME`: Global handle to the primary created CPU target object (e.g., `stm32f1x.cpu`).
- **Temporary Variables**: Variables prefixed with a leading underscore (e.g., `_CHIPNAME`, `_CPUTAPID`) are temporary local variables within scripts.

### 13.3 Structured Execution: `init_targets` and `init_board` Procedures
To avoid fragile procedural order dependencies in linear scripts, OpenOCD supports structured procedures:
- `init_targets`: Encapsulates target-specific initialization (declaring internal flash and RAM). Can be overridden by downstream scripts for derivative chips.
- `init_board`: Executed upon entering the run stage. Configures board-specific items (reset signals, clock setup, and `reset-init` handlers) after targets are instantiated.

### 13.4 Translating Proprietary Debugger Scripts
Scripts from proprietary systems (Lauterbach TRACE32, Abatron BDI2000/3000, Segger J-Link, TI Code Composer Studio) map directly to OpenOCD primitives:
- Lauterbach `Data.Set <addr> %long <val>` -> `mww <addr> <val>`
- Lauterbach `Register.Set PC <val>` -> `reg pc <val>`
- TRACE32 coprocessor writes -> `arm mcr <coproc> <op1> <CRn> <CRm> <op2> <val>`

---

## 14. The Jim-Tcl Scripting Engine & RPC Server

### 14.1 Jim-Tcl Core Philosophy: Strings, Quoting, and Non-Existent Control Flow
OpenOCD embeds Jim-Tcl, a lightweight, highly efficient implementation of Tcl:
1. **Rule #1: Everything is a String**: Numbers, lists, code blocks, and commands are represented and passed as strings.
2. **Rule #2: Control Flow Does Not Exist**: Keywords like `for`, `while`, `if`, and `proc` are standard Tcl commands that take code blocks as string parameters.
3. **Quoting Rules**:
   - `[square brackets]`: Command substitution (executes immediately and returns the result string).
   - `"double quotes"`: Text interpolation ($variables and [commands] are expanded immediately at parse time).
   - `{curly braces}`: Deferred literal evaluation (contents are preserved verbatim without variable or command expansion).

### 14.2 Variable Scoping, Dynamic Command Creation, and Macro Constructs
- Inside a `proc`, variables are strictly local unless declared with `global <varname>`.
- Procs can dynamically generate custom commands and procedures using `foreach` and `format`:
```tcl
foreach reg {r0 r1 r2 r3} {
    proc dump_$reg {} [format "reg %s" $reg]
}
```

### 14.3 Headless Machine Interface: The Tcl RPC Protocol & Async Notifications
Clients connect to TCP port 6666 to control OpenOCD programmatically:
- Send arbitrary Tcl commands terminated by byte `0x1a`.
- OpenOCD executes the command and returns the response terminated by `0x1a`.
- **Asynchronous Notifications**: When enabled via `tcl_notifications on`, OpenOCD pushes unprompted status updates whenever target state changes:
```tcl
type target_event event halted
type target_state state halted
type target_reset mode halt
```

---

## 15. Operational Playbook & Troubleshooting Encyclopedia (FAQ)

### 15.1 Clock Synchronization & Adaptive Clocking Nuances
- **Symptom**: `JTAG-DP STICKY ERROR` or random scan chain verification failures.
- **Root Cause**: JTAG clock speed exceeds 1/6th of internal core frequency.
- **Fix**: Use `jtag_rclk <fallback_speed_khz>` to enable adaptive clocking, or set `adapter speed 100` before reset and ramp to `adapter speed 8000` only inside the `reset-init` handler.

### 15.2 Handling Low-Power States, Sleep Modes, and `WFI` Instruction Pitfalls
- **Symptom**: Debugger loses connection immediately after CPU starts executing code; `halt` fails.
- **Root Cause**: Core executed `WFI` (Wait For Interrupt) or entered deep sleep (Stop/Standby). On ARM, gating core clocks freezes JTAG synchronization logic.
- **Fix**:
  1. Configure debug-in-sleep control registers inside target configuration (e.g., set `DBGMCU_CR |= DBG_SLEEP | DBG_STOP | DBG_STANDBY` on STM32).
  2. For early firmware, add a 1-second delay loop immediately following the reset handler before sleep modes are activated.
  3. Connect using `reset_config connect_assert_srst` to halt before the core executes `WFI`.

### 15.3 Watchdog Management During Halt-Mode Debugging
- **Symptom**: Target resets spontaneously a few milliseconds after being halted.
- **Root Cause**: Independent hardware watchdog continues counting while the core is halted.
- **Fix**: Configure target registers in `reset-init` to freeze watchdog timers during debug halt (e.g., `kinetis disable_wdog`, or configure STM32 `DBGMCU_APB1_FZ`).

### 15.4 GDB Stack Frame Climbing and Non-Fatal Data Aborts
- **Symptom**: GDB issues repetitive `arm7_9_read_memory(): memory read caused data abort` errors upon connecting.
- **Root Cause**: GDB attempts to backtrace past the root stack frame (`main` or reset handler) by reading invalid high memory addresses.
- **Fix**: In the target startup assembly, initialize the stack frame by pushing 8 registers of zeroes (`0x00000000`) before calling `main()`, giving GDB an unambiguous boundary to terminate stack unwinding.

### 15.5 Broken Reset Layouts & JTAG Scan Chain Failures
- **Symptom**: Scan chain fails validation after `reset halt`.
- **Root Cause**: SRST and TRST lines are shorted or pull-down resistors are too weak, causing transient spikes.
- **Fix**: Specify `reset_config trst_and_srst srst_pulls_trst` in the board configuration to instruct OpenOCD to handle the signal dependency correctly.
