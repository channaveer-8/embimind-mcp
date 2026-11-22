# OpenOCD Exhaustive Command & Driver Reference Manual
**Open On-Chip Debugger (Release 0.12.0)**  
*Complete, Unabridged Reference of All Commands, Config Commands, Drivers, Options, and Procedures*

---

## Master Table of Contents
1. [Server, Daemon & Startup Commands](#1-server-daemon--startup-commands)
2. [Debug Adapter & Interface Driver Commands](#2-debug-adapter--interface-driver-commands)
   - 2.1 Generic Adapter Configuration
   - 2.2 FTDI / MPSSE Interface Driver (`ftdi`)
   - 2.3 FT232R UART Bitbang Driver (`ft232r`)
   - 2.4 ARM CMSIS-DAP Driver (`cmsis-dap`)
   - 2.5 SEGGER J-Link Driver (`jlink`)
   - 2.6 STMicroelectronics ST-LINK Direct DAP Driver (`st-link`)
   - 2.7 High Level Adapter Driver (`hla`)
   - 2.8 Cypress KitProg Driver (`kitprog`)
   - 2.9 Parallel Port Driver (`parport`) & Hardware Accelerators (`amt_jtagaccel`, `gw16012`)
   - 2.10 Bus Pirate Driver (`buspirate`)
   - 2.11 Espressif USB JTAG Driver (`esp_usb_jtag`)
   - 2.12 Texas Instruments XDS110 Driver (`xds110`)
   - 2.13 Xilinx PCIe Virtual Cable (`xlnx_pcie_xvc`)
   - 2.14 Direct Memory-Mapped GPIO Drivers (`bcm2835gpio`, `am335xgpio`, `imx_gpio`)
   - 2.15 Linux GPIO Drivers (`linuxgpiod`, `sysfsgpio`)
   - 2.16 OpenJTAG Driver (`openjtag`)
   - 2.17 Simulation & Emulation Drivers (`vdebug`, `jtag_dpi`, `remote_bitbang`)
   - 2.18 Altera USB-Blaster Driver (`usb_blaster`)
   - 2.19 Miscellaneous USB & Dongle Drivers (`presto`, `rlink`, `usbprog`, `vsllink`, `ulink`, `arm-jtag-ew`, `opendous`, `at91rm9200`, `ep93xx`, `dummy`)
3. [Transport Configuration Commands](#3-transport-configuration-commands)
4. [Reset Configuration & Control Commands](#4-reset-configuration--control-commands)
5. [JTAG TAP & Scan Chain Declaration Commands](#5-jtag-tap--scan-chain-declaration-commands)
6. [ARM Debug Access Port (DAP) Declaration & Commands](#6-arm-debug-access-port-dap-declaration--commands)
   - 6.1 Global DAP Commands
   - 6.2 DAP Instance Subcommands (`$dap_name`)
7. [CPU & Target Management Commands](#7-cpu--target-management-commands)
   - 7.1 Target Creation & Management
   - 7.2 Target Configuration Options (`$target_name configure`)
   - 7.3 Target Object Commands (`$target_name`)
8. [Target Run Control, Memory Access, & Image Operations](#8-target-run-control-memory-access--image-operations)
   - 8.1 Target Execution & State Control
   - 8.2 Memory Inspection & Modification Primitives
   - 8.3 CPU Register Commands
   - 8.4 Binary & Hex Image Loading/Dumping
   - 8.5 Breakpoints & Watchpoints
   - 8.6 Real Time Transfer (RTT)
   - 8.7 Profiling & Utility Commands
9. [Flash Subsystem & Driver-Specific Commands](#9-flash-subsystem--driver-specific-commands)
   - 9.1 General NOR Flash Commands
   - 9.2 External NOR Flash Drivers (`cfi`, `jtagspi`, `xcf`, `lpcspifi`, `stmsmi`, `stmqspi`, `mrvlqspi`, `ath79`, `fespi`, `virtual`)
   - 9.3 Microcontroller Internal Flash Drivers & Controller Commands:
     - 9.3.1 Microchip / Atmel (`at91samd`, `atsame5`, `at91sam3`, `at91sam4`, `at91sam4l`, `atsamv`, `at91sam7`, `aduc702x`)
     - 9.3.2 STMicroelectronics (`stm32f1x`, `stm32f2x`, `stm32h7x`, `stm32lx`, `stm32l4x`, `bluenrg-x`, `str7x`, `str9x`, `str9xpec`)
     - 9.3.3 NXP / Freescale (`kinetis`, `kinetis_ke`, `lpc2000`, `lpc288x`, `lpc2900`)
     - 9.3.4 Cypress (`psoc4`, `psoc5lp`, `psoc5lp_eeprom`, `psoc5lp_nvl`, `psoc6`)
     - 9.3.5 Texas Instruments (`cc26xx`, `cc3220sf`, `stellaris`, `msp432`, `tms470`)
     - 9.3.6 Nordic Semiconductor (`nrf5`)
     - 9.3.7 Silicon Labs (`efm32`, `sim3x`)
     - 9.3.8 Raspberry Pi & Onsemi (`rp2040`, `rsl10`)
     - 9.3.9 Fujitsu / Spansion (`fm3`, `fm4`)
     - 9.3.10 Infineon (`xmc1xxx`, `xmc4xxx`)
     - 9.3.11 Other Vendors (`ambiqmicro`, `mdr`, `niietcm4`, `npcx`, `pic32mx`, `swm050`, `w600`, `esirisc`, `ocl`, `avr`)
10. [NAND Flash Commands & Drivers](#10-nand-flash-commands--drivers)
    - 10.1 General NAND Commands
    - 10.2 NAND Controller Drivers (`at91sam9`, `davinci`, `lpc3180`, `mx3`, `mxc`, `orion`, `s3c24xx`)
11. [PLD / FPGA Configuration Commands](#11-pld--fpga-configuration-commands)
12. [Architecture & Core-Specific Commands](#12-architecture--core-specific-commands)
    - 12.1 ARM Hardware Tracing (ETM, ETB, Trace Port Drivers)
    - 12.2 ARM CoreSight Cross-Trigger Interface (CTI)
    - 12.3 Generic ARM Commands
    - 12.4 ARMv4 and ARMv5 Specific Commands (ARM7, ARM9, ARM920T, ARM926EJ-S, ARM966E, XScale)
    - 12.5 ARMv6 Architecture (ARM11)
    - 12.6 ARMv7-A and ARMv7-R Architectures
    - 12.7 ARM CoreSight TPIU, SWO, and ITM Stimulus
    - 12.8 ARMv7-M & Cortex-M Specific Commands
    - 12.9 ARMv8-A (AArch64) Architecture
    - 12.10 RISC-V Architecture
    - 12.11 Cadence / Tensilica Xtensa Architecture
    - 12.12 Synopsys ARC Architecture
    - 12.13 EnSilica eSi-RISC Architecture
    - 12.14 Intel Quark (IA-32 / x86) Architecture
    - 12.15 OpenRISC 1000 Architecture
    - 12.16 Software Tracing & DCC Messages (`libdcc`)
13. [Low-Level JTAG & Boundary Scan Commands](#13-low-level-jtag--boundary-scan-commands)
    - 13.1 Low-Level JTAG Scan Operations
    - 13.2 Boundary Scan Test (SVF, XSVF, IPDBG)
14. [RAM Testing & Firmware Recovery Utilities](#14-ram-testing--firmware-recovery-utilities)
15. [GDB Configuration & Server Control Commands](#15-gdb-configuration--server-control-commands)
16. [Jim-Tcl Scripting API & RPC Server Commands](#16-jim-tcl-scripting-api--rpc-server-commands)

---

## Typographical Conventions & Command Classification
Every command in this reference is categorized by its execution stage:
- **`[Command]`**: General execution command; typically callable at any time or during the Run stage via Telnet, GDB (`monitor <cmd>`), or Tcl scripts.
- **`[Config Command]`**: Configuration-stage only command; must be declared in configuration files or passed on the command line prior to server initialization (`init`).
- **`[Overridable Procedure]`**: Built-in Jim-Tcl procedure that can be overridden by user scripts to customize standard reset or startup behaviors.
- **`[Function]`**: Built-in Jim-Tcl helper function.
- **`[Interface Driver]` / `[Flash Driver]` / `[NAND Driver]` / `[FPGA Driver]` / `[Trace Port Driver]`**: Driver identifiers passed to registration commands like `adapter driver`, `flash bank`, `nand device`, etc.

---
## 1. Server, Daemon & Startup Commands

### command mode
- **Syntax**: `command mode [command_name]`
- **Mode**: `[Command]` (Valid at any time)
- **Description**: Returns the execution stage allowed for a given command: `'any'`, `'config'`, or `'exec'`. If `command_name` is omitted, returns the current server execution mode. If an unknown command is supplied, returns `'unknown'`.
- **Example**:
  ```tcl
  command mode adapter driver
  # Returns: config
  command mode poll
  # Returns: exec
  ```

### init
- **Syntax**: `init`
- **Mode**: `[Config Command]`
- **Description**: Explicitly terminates the configuration stage and transitions OpenOCD into the run stage. This command validates the configured JTAG scan chain, probes hardware, initializes targets, DAPs, flash controllers, and starts server listeners. If omitted in configuration scripts, OpenOCD calls `init` implicitly at the conclusion of script parsing.
- **Internal Chain**: `init` automatically executes the following subsystem initializers:
  1. `target init` `[Config Command]`
  2. `transport init` `[Command]`
  3. `dap init` `[Command]`
  4. `flash init` `[Config Command]`
  5. `nand init` `[Config Command]`
  6. `pld init` `[Config Command]`
  7. `tpiu init` `[Command]`
  8. Evaluates all callbacks in the `post_init_commands` Tcl list.
- **Example**:
  ```tcl
  # Force early run-stage entry to read memory or write flash in a batch script:
  init
  reset init
  flash write_image erase firmware.bin 0x08000000
  exit
  ```

### noinit
- **Syntax**: `noinit`
- **Mode**: `[Config Command]`
- **Description**: Disables the automatic implicit execution of `init` at the conclusion of startup script processing. Allows developers to connect over Telnet or Tcl while OpenOCD remains in the configuration stage to issue interactive configuration commands. The user must manually call `init` to start debugging.

### jtag_init
- **Syntax**: `jtag_init`
- **Mode**: `[Overridable Procedure]`
- **Description**: Invoked during server startup to verify communication with the configured JTAG scan chain. The default implementation first runs `jtag arp_init` (lightweight reset). If validation fails, it invokes `init_reset` for a full reset before re-examining the chain.

### gdb_port
- **Syntax**: `gdb_port [number | "pipe" | "disabled" | path]`
- **Mode**: `[Config Command]`
- **Description**: Queries or configures the TCP port for GDB connections.
  - Omitted argument: Displays currently configured GDB port.
  - `<number>`: Base port (default: `3333`). Core 0 listens on base port, core 1 on `base + 1`, etc.
  - `"pipe"`: Direct communication over stdin/stdout pipes (useful when GDB spawns OpenOCD).
  - `"disabled"`: Deactivates GDB server functionality entirely.
  - `<path>`: Named pipe path (output pipe gets `'o'` appended).

### telnet_port
- **Syntax**: `telnet_port [number | "disabled"]`
- **Mode**: `[Config Command]`
- **Description**: Queries or specifies the TCP port on which OpenOCD listens for incoming interactive Telnet connections (intended for human operators). Default port is `4444`. Set to `"disabled"` to deactivate.

### tcl_port
- **Syntax**: `tcl_port [number | "disabled"]`
- **Mode**: `[Config Command]`
- **Description**: Queries or configures the TCP port for headless Tcl RPC client connections (intended for machine interfaces, automated test frameworks, and IDE plugins). Default port is `6666`. Set to `"disabled"` to deactivate.

### bindto
- **Syntax**: `bindto [name]`
- **Mode**: `[Config Command]`
- **Description**: Specifies the IPv4 network interface or hostname to which TCP servers (GDB, Telnet, Tcl) bind. By default, OpenOCD binds strictly to `127.0.0.1` (loopback) for security. Use `bindto 0.0.0.0` to permit remote network connections across a local network.

### shutdown
- **Syntax**: `shutdown [error]`
- **Mode**: `[Command]`
- **Description**: Gracefully shuts down the OpenOCD daemon, disconnecting all active GDB, Telnet, and RPC sessions. If `error` is specified, OpenOCD exits with a non-zero exit code. Triggers all callbacks registered in the `pre_shutdown_commands` Tcl list.
- **Example**:
  ```tcl
  lappend pre_shutdown_commands { echo "Session complete. Turning off power." }
  shutdown
  ```

### exit
- **Syntax**: `exit`
- **Mode**: `[Command]`
- **Description**: Closes the current interactive Telnet session without shutting down the OpenOCD server process.

### help / usage
- **Syntax**: `help [string]` / `usage [string]`
- **Mode**: `[Command]`
- **Description**: Displays command help strings or parameter usage text. If `string` is supplied, filters output to matching commands.

### sleep
- **Syntax**: `sleep msec [busy]`
- **Mode**: `[Command]`
- **Description**: Suspends script execution for at least `msec` milliseconds. If `busy` is specified, executes a tight spinloop instead of releasing the CPU (strongly discouraged).

### debug_level
- **Syntax**: `debug_level [n]`
- **Mode**: `[Command]`
- **Description**: Displays or sets the verbosity level of server logging (0 to 4):
  - `0`: Errors only
  - `1`: Warnings and errors
  - `2`: Informational messages (default)
  - `3`: Debugging messages
  - `4`: Verbose low-level communication tracing

### echo
- **Syntax**: `echo [-n] message`
- **Mode**: `[Command]`
- **Description**: Prints `message` to the server log and active Telnet session at user priority. `-n` suppresses the trailing newline.

### log_output
- **Syntax**: `log_output [filename | "default"]`
- **Mode**: `[Command]`
- **Description**: Redirects logging messages to a file, or restores default output (`stderr`).

### add_script_search_dir
- **Syntax**: `add_script_search_dir [directory]`
- **Mode**: `[Command]`
- **Description**: Appends `directory` to OpenOCD's search path for configuration scripts and auxiliary data files.

### find / ocd_find
- **Syntax**: `find <filename>` / `ocd_find <filename>`
- **Mode**: `[Command]`
- **Description**: Resolves and returns the full absolute path to `<filename>` by evaluating OpenOCD's search directories in priority order.

---
## 2. Debug Adapter & Interface Driver Commands

### 2.1 Generic Adapter Configuration

#### adapter driver
- **Syntax**: `adapter driver name`
- **Mode**: `[Config Command]`
- **Description**: Selects the interface driver used to communicate with the target hardware debug adapter.

#### adapter list
- **Syntax**: `adapter list`
- **Mode**: `[Command]`
- **Description**: Returns the list of all adapter drivers compiled into the running OpenOCD binary.

#### adapter name
- **Syntax**: `adapter name`
- **Mode**: `[Command]`
- **Description**: Returns the name of the currently active debug adapter driver.

#### adapter transports
- **Syntax**: `adapter transports transport_name+`
- **Mode**: `[Config Command]`
- **Description**: Declares the physical transport layers supported by the adapter hardware (e.g., `jtag`, `swd`, `swim`). Used to restrict or override driver defaults when external hardware (jumpers, level shifters) limits capability.

#### adapter speed
- **Syntax**: `adapter speed max_speed_kHz`
- **Mode**: `[Command]`
- **Description**: Sets the maximum clock frequency of the adapter interface in kHz (e.g., `3000` for 3 MHz). Value `0` enables adaptive clocking (RTCK) if supported by the adapter and target.
- **Example**: `adapter speed 4000`

#### adapter serial
- **Syntax**: `adapter serial serial_string`
- **Mode**: `[Config Command]`
- **Description**: Matches the debug adapter by its USB serial number string when multiple identical adapters are plugged into the host.

#### adapter usb location
- **Syntax**: `adapter usb location [<bus>-<port>[.<port>]...]`
- **Mode**: `[Config Command]`
- **Description**: Binds to a specific physical USB port based on hub topology path (e.g., `1-1.2`). Requires libusb 1.0.16+.

#### adapter gpio
- **Syntax**: `adapter gpio [ tdo | tdi | tms | tck | trst | swdio | swdio_dir | swclk | srst | led [ gpio_number | -chip chip_number | -active-high | -active-low | -push-pull | -open-drain | -open-source | -pull-none | -pull-up | -pull-down | -init-inactive | -init-active | -init-input ] ]`
- **Mode**: `[Config Command]`
- **Description**: Provides unified, generic GPIO mapping for bitbanging and SoC GPIO adapters. Configures signal direction, active polarity, output drive stage, pull resistors, and initial states.

---

### 2.2 FTDI / MPSSE Interface Driver (`ftdi`)
Driver for high-speed USB adapters utilizing FTDI FT2232, FT4232, and FT232H MPSSE engines via direct asynchronous libusb-1.0.

- `ftdi vid_pid [vid pid]+`: `[Config Command]` Specifies up to eight USB VID/PID pairs to identify the adapter. Example: `ftdi vid_pid 0x0403 0x6010`.
- `ftdi device_desc description`: `[Config Command]` Matches USB device string descriptor (`iProduct`).
- `ftdi channel channel`: `[Config Command]` Selects FTDI chip channel (typically channel `0`, channel `1` for secondary).
- `ftdi layout_init data direction`: `[Config Command]` Sets initial 16-bit values for FTDI GPIO data and direction registers.
- `ftdi layout_signal name [-data|-ndata data_mask] [-input|-ninput input_mask] [-oe|-noe oe_mask] [-alias|-nalias name]`: `[Command]` Defines logical control signals (`nTRST`, `nSRST`, `SWD_EN`, `SWDIO_OE`, `LED`) tied to specific GPIO bitmasks and buffer configurations.
- `ftdi set_signal name 0|1|z`: `[Command]` Directly forces a previously defined signal to logic low (`0`), logic high (`1`), or high impedance (`z`).
- `ftdi get_signal name`: `[Command]` Reads the logic level of a defined input signal.
- `ftdi tdo_sample_edge rising|falling`: `[Command]` Configures whether TDO is sampled on the rising (default) or falling edge of TCK to compensate for round-trip propagation delays at high clock frequencies.

---

### 2.3 FT232R UART Bitbang Driver (`ft232r`)
Reuses RS-232 modem lines on FTDI USB UART bridge chips (FT232R, FT230X, FT231X) as bitbanged JTAG pins.

- `ft232r vid_pid vid pid`: `[Config Command]` Adapter USB VID and PID (default `0x0403:0x6001`).
- `ft232r jtag_nums tck tms tdi tdo`: `[Config Command]` Assigns all four primary JTAG GPIO line numbers at once.
- `ft232r tck_num tck` / `tms_num tms` / `tdi_num tdi` / `tdo_num tdo`: `[Config Command]` Configures individual line bit numbers.
- `ft232r trst_num trst` / `srst_num srst`: `[Config Command]` Configures TRST and SRST bit numbers.
- `ft232r restore_serial word`: `[Config Command]` 16-bit control word restoring normal serial port pinout on exit.

---

### 2.4 ARM CMSIS-DAP Driver (`cmsis-dap`)
Supports standard ARM CMSIS-DAP probes in v1 (USB HID) and v2 (USB Bulk) protocols.

- `cmsis_dap_vid_pid [vid pid]+`: `[Config Command]` Up to eight VID/PID pairs.
- `cmsis_dap_backend [auto|usb_bulk|hid]`: `[Config Command]` Selects communication backend. Default `auto` attempts bulk then falls back to HID.
- `cmsis_dap_usb interface [number]`: `[Config Command]` Specifies USB interface number for v2 bulk mode.
- `cmsis-dap info`: `[Command]` Queries firmware version, hardware capabilities, and bus status.
- `cmsis-dap cmd number number ...`: `[Command]` Transmits arbitrary raw CMSIS-DAP packet bytes for vendor extensions or testing.

---

### 2.5 SEGGER J-Link Driver (`jlink`)
Supports official SEGGER J-Link and OEM clones (SAM-ICE, IAR J-Link) over JTAG and SWD.

- `jlink hwstatus`: `[Command]` Queries target voltage, pin states, and hardware metrics.
- `jlink freemem`: `[Command]` Displays available internal memory in the probe.
- `jlink jtag [2|3]`: `[Command]` Selects internal JTAG command protocol version.
- `jlink config`: `[Command]` Displays nonvolatile probe configuration.
- `jlink config targetpower [on|off]`: `[Command]` Toggles 5V target power output on JTAG pin 19.
- `jlink config mac [ff:ff:ff:ff:ff:ff]`: `[Command]` Sets probe Ethernet MAC address.
- `jlink config ip [A.B.C.D(/E|F.G.H.I)]`: `[Command]` Sets static IP configuration for networked J-Links.
- `jlink config usb [0 to 3]`: `[Command]` Configures probe USB address / PID offset.
- `jlink config reset` / `jlink config write`: `[Command]` Resets or commits configuration to non-volatile storage.
- `jlink emucom write <channel> <data>` / `jlink emucom read <channel> <length>`: `[Command]` Bidirectional communication over SEGGER EMUCOM channels.
- `jlink usb <0 to 3>`: `[Config Command]` USB address selection before init.

---

### 2.6 STMicroelectronics ST-LINK Direct DAP Driver (`st-link`)
Direct ADIv5 DAP access driver for ST-LINK/V2 (firmware >= V2J24) and STLINK-V3.

- `st-link backend (usb | tcp [port])`: `[Config Command]` Chooses exclusive USB access or shared TCP connection via `st-link-server` (default port `7184`).
- `st-link vid_pid [vid pid]+`: `[Config Command]` Specifies adapter VID/PID pairs.
- `st-link cmd rx_n (tx_byte)+`: `[Command]` Sends arbitrary sequence of raw bytes and reads `rx_n` bytes response (useful for reading target supply voltage or options).

---

### 2.7 High Level Adapter Driver (`hla`)
Abstract driver for probes with encapsulated target control firmware (ST-LINK v1/v2, TI ICDI, Nuvoton Nu-Link).

- `hla_layout (stlink|icdi|nulink)`: `[Config Command]` Specifies the high-level adapter protocol layout.
- `hla_vid_pid [vid pid]+`: `[Config Command]` USB VID and PID definitions.
- `hla_stlink_backend (usb | tcp [port])`: `[Config Command]` Shared server or direct USB backend selection.
- `hla_command command`: `[Command]` Forwards custom raw strings to the layout handler.
- `hla_device_desc description`: `[Config Command]` Device description string.

---

### 2.8 Cypress KitProg Driver (`kitprog`)
Driver for Cypress PSoC and PRoC KitProg adapters operating in proprietary SWD mode.

- `kitprog_init_acquire_psoc`: `[Config Command]` Runs hard acquisition sequence during adapter init.
- `kitprog acquire_psoc`: `[Command]` Executes target acquisition sequence immediately (hard-resets target).
- `kitprog info`: `[Command]` Displays KitProg hardware version, firmware version, and target voltage.

---

### 2.9 Parallel Port Driver (`parport`) & Hardware Accelerators
- `parport cable name`: `[Config Command]` Sets cable layout (`wiggler`, `wiggler2`, `wiggler_ntrst_inverted`, `dlc5`, `arm-jtag`, `chameleon`, `flashlink`, `lattice`, `altium`, `triton`).
- `parport port [port_number]`: `[Config Command]` Specifies parallel port I/O address (e.g., `0x378` for LPT1) or `/dev/parport` device index.
- `parport toggling_time [nanoseconds]`: `[Config Command]` Calibrates TCK transition delay in nanoseconds.
- `parport write_on_exit (on|off)`: `[Config Command]` Writes a safe neutral bit pattern to the parallel pins upon exit.
- `amt_jtagaccel`: `[Interface Driver]` Amontec Chameleon parallel port accelerator.
  - `amt_jtagaccel rtck [enable|disable]`: `[Config Command]` Toggles RTCK sampling.
- `gw16012`: `[Interface Driver]` Gateworks GW16012 parallel JTAG programmer.

---

### 2.10 Bus Pirate Driver (`buspirate`)
- `buspirate port serial_port`: `[Config Command]` Serial COM port path (e.g., `/dev/ttyUSB0` or `COM3`).
- `buspirate speed (normal|fast)`: `[Config Command]` Sets UART baud to 115.2 kbps (`normal`) or 1 Mbps (`fast`).
- `buspirate mode (normal|open-drain)`: `[Config Command]` Configures push-pull vs. open-drain outputs.
- `buspirate pullup (0|1)`: `[Config Command]` Connects internal pull-up resistors to target VREF.
- `buspirate vreg (0|1)`: `[Config Command]` Enables built-in 3.3V / 5V power supply regulators.
- `buspirate led (0|1)`: `[Command]` Toggles Bus Pirate user LED.

---

### 2.11 Espressif USB JTAG Driver (`esp_usb_jtag`)
Internal USB-JTAG bridge on ESP32-C3 and ESP32-S3 chips via direct USB D+/D- pins.

- `espusbjtag vid_pid vid pid`: `[Config Command]` USB VID and PID (default `0x303a:0x1001`).
- `espusbjtag caps_descriptor caps_descriptor`: `[Config Command]` Sets JTAG descriptor to read hardware capabilities.
- `espusbjtag chip_id chip_id`: `[Config Command]` Target chip ID for ESP USB Bridge.
- `espusbjtag tdo`: `[Command]` Returns physical logic state of TDO line.
- `espusbjtag setio setio`: `[Command]` Manually drives JTAG output lines in order `(tdi tms tck trst srst)`.

---

### 2.12 Texas Instruments XDS110 Driver (`xds110`)
- `xds110 supply voltage_in_millivolts`: `[Config Command]` Powers target board from probe between 1800 mV and 3600 mV (`0` disables).
- `xds110 info`: `[Command]` Displays probe firmware version and serial number.

---

### 2.13 Xilinx PCIe Virtual Cable (`xlnx_pcie_xvc`)
- `xlnx_pcie_xvc config device`: `[Config Command]` Specifies PCIe device string (e.g., `0000:65:00.1`) exposing JTAG/SWD over PCI Express capability registers.

---

### 2.14 Direct Memory-Mapped GPIO Drivers
Direct register access on single-board computer SoC expansion headers:
- `bcm2835gpio`: Raspberry Pi driver.
  - `bcm2835gpio peripheral_base base`: `[Config Command]` Base address for GPIO registers (`0x20000000` for RPi1, `0x3F000000` for RPi2/3, `0xFE000000` for RPi4).
  - `bcm2835gpio speed_coeffs speed_coeff speed_offset`: `[Config Command]` Delay calculation tuning.
- `am335xgpio`: BeagleBone Black / Green driver.
  - `am335xgpio speed_coeffs speed_coeff speed_offset`: `[Config Command]` Delay calculation parameters.
- `imx_gpio`: NXP i.MX SoC GPIO driver.

---

### 2.15 Linux GPIO Drivers
- `linuxgpiod`: `[Interface Driver]` Uses Linux `libgpiod` userspace GPIO character device API. All pin assignments handled via `adapter gpio`.
- `sysfsgpio`: `[Interface Driver]` Legacy sysfs GPIO driver (deprecated since Linux kernel 5.3).

---

### 2.16 OpenJTAG Driver (`openjtag`)
- `openjtag variant variant`: `[Config Command]` Variant type (`standard` or `cy7c65215`).
- `openjtag device_desc string`: `[Config Command]` USB descriptor string.

---

### 2.17 Simulation & Emulation Drivers
- `vdebug`: Cadence virtual debug interface driver.
  - `vdebug server host:port`: `[Config Command]` Server hostname and TCP port.
  - `vdebug batching value`: `[Config Command]` Batch mode (`0` = none, `1` = batch writes, `2` = batch reads and writes).
  - `vdebug polling min max`: `[Config Command]` Polling intervals in milliseconds.
  - `vdebug bfm_path path clk_period`: `[Config Command]` Verilog BFM hierarchy path and clock period (e.g., `40ns`).
  - `vdebug mem_path path base size`: `[Config Command]` Verilog backdoor memory instance path, base address, and byte size.
- `jtag_dpi`: SystemVerilog Direct Programming Interface client driver.
  - `jtag_dpi set_address address` / `jtag_dpi set_port port`: `[Config Command]` Address and TCP port for DPI server.
- `remote_bitbang`: Bridges JTAG transitions over TCP/Unix sockets to simulators.
  - `remote_bitbang host hostname` / `remote_bitbang port number`: `[Config Command]` Port number (`0` selects Unix socket).

---

### 2.18 Altera USB-Blaster Driver (`usb_blaster`)
- `usb_blaster vid_pid vid pid`: `[Config Command]` Device VID/PID (default `0x09FB:0x6001`).
- `usb_blaster pin (pin6|pin8) (0|1|s|t)`: `[Command]` Assigns unused header pins as SRST (`s`) or TRST (`t`).
- `usb_blaster lowlevel_driver (ftdi|ublast2)`: `[Config Command]` Selects low-level access driver.
- `usb_blaster firmware path`: `[Config Command]` Path to firmware for USB-Blaster II.

---

### 2.19 Miscellaneous USB & Dongle Drivers
- `presto`: `[Interface Driver]` ASIX PRESTO USB JTAG programmer.
- `rlink`: `[Interface Driver]` Raisonance RLink USB adapter.
- `usbprog`: `[Interface Driver]` Usbprog freely programmable open-hardware USB adapter.
- `vsllink`: `[Interface Driver]` Versaloon USB multi-protocol programmer.
- `ulink`: `[Interface Driver]` Keil ULINK v1 JTAG debugger.
- `arm-jtag-ew`: `[Interface Driver]` Olimex ARM-JTAG-EW USB probe.
  - `armjtagew_info`: `[Command]` Displays probe internal diagnostics.
- `opendous`: `[Interface Driver]` Opendous USB JTAG adapter (AT90USB162).
- `at91rm9200`: `[Interface Driver]` Bitbanging from Atmel AT91RM9200 processor GPIOs.
- `ep93xx`: `[Interface Driver]` Bitbanging from Cirrus Logic EP93xx processor GPIOs.
- `dummy`: `[Interface Driver]` Software-only dummy driver for simulator testing and headless validation.

---
## 3. Transport Configuration Commands

### transport list
- **Syntax**: `transport list`
- **Mode**: `[Command]`
- **Description**: Displays the names of all transport protocols supported by the current OpenOCD build.

### transport select
- **Syntax**: `transport select [transport_name]`
- **Mode**: `[Command]`
- **Description**: Selects the active transport for the session (e.g., `jtag`, `swd`, `swim`, `spi`, `hla_jtag`, `hla_swd`, `dapdirect_jtag`, `dapdirect_swd`). If called without arguments, queries and returns the name of the active transport.

### swd newdap
- **Syntax**: `swd newdap <chipname> <tapname> [options]`
- **Mode**: `[Config Command]`
- **Description**: Declares an SWD Debug Access Point (DAP).

### swim newtap
- **Syntax**: `swim newtap <basename> <tap_type>`
- **Mode**: `[Config Command]`
- **Description**: Creates a virtual SWIM TAP required by OpenOCD's target engine for STM8 targets.

### jtag_rclk
- **Syntax**: `jtag_rclk fallback_speed_kHz`
- **Mode**: `[Function]`
- **Description**: Attempts to enable adaptive clocking (RTCK). If unsupported by the adapter or target, falls back to `fallback_speed_kHz`.

---
## 4. Reset Configuration & Control Commands

### reset_config
- **Syntax**: `reset_config [signals] [combination] [gates] [connect_type] [trst_type] [srst_type]`
- **Mode**: `[Command]`
- **Description**: Defines reset line capabilities and behavior for the board/target:
  - `signals`: `none`, `trst_only`, `srst_only`, `trst_and_srst`.
  - `combination`: `separate` (default), `srst_pulls_trst`, `trst_pulls_srst`, `combined`.
  - `gates`: `srst_gates_jtag` (default: JTAG clock stopped during SRST), `srst_nogate`.
  - `connect_type`: `connect_deassert_srst` (default), `connect_assert_srst` (holds SRST low during connection).
  - `trst_type`: `trst_push_pull` (default), `trst_open_drain`.
  - `srst_type`: `srst_open_drain` (default), `srst_push_pull`.
- **Example**: `reset_config trst_and_srst srst_pulls_trst srst_gates_jtag`

### adapter srst delay
- **Syntax**: `adapter srst delay milliseconds`
- **Mode**: `[Command]`
- **Description**: Delay in milliseconds to wait after deasserting `nSRST` before starting JTAG/SWD operations (allows debouncing and power stabilization).

### adapter srst pulse_width
- **Syntax**: `adapter srst pulse_width milliseconds`
- **Mode**: `[Command]`
- **Description**: Minimum duration in milliseconds to hold `nSRST` asserted.

### jtag_ntrst_delay
- **Syntax**: `jtag_ntrst_delay milliseconds`
- **Mode**: `[Command]`
- **Description**: Delay in milliseconds after deasserting `nTRST` before beginning new JTAG operations.

### jtag_ntrst_assert_width
- **Syntax**: `jtag_ntrst_assert_width milliseconds`
- **Mode**: `[Command]`
- **Description**: Minimum time in milliseconds to hold `nTRST` asserted.

### adapter assert / adapter deassert
- **Syntax**: `adapter assert [srst | trst]` / `adapter deassert [srst | trst]`
- **Mode**: `[Command]`
- **Description**: Manually forces the specified reset signal line into asserted or deasserted state. With no arguments, queries signal status.

### init_reset
- **Syntax**: `init_reset mode`
- **Mode**: `[Overridable Procedure]`
- **Description**: Executed near the beginning of the `reset` command sequence to provide a cold power-up reset. Default invokes `jtag arp_init-reset`.

### jtag arp_init
- **Syntax**: `jtag arp_init`
- **Mode**: `[Command]`
- **Description**: Low-level scan chain validator using TMS/TCK/TDI/TDO without SRST/TRST. Verifies IDCODEs and instruction registers.

### jtag arp_init-reset
- **Syntax**: `jtag arp_init-reset`
- **Mode**: `[Command]`
- **Description**: Asserts physical TRST and SRST lines before executing `jtag arp_init`.

---
## 5. JTAG TAP & Scan Chain Declaration Commands

### jtag newtap
- **Syntax**: `jtag newtap chipname tapname configparams...`
- **Mode**: `[Config Command]`
- **Description**: Declares a new Test Access Port on the JTAG scan chain with dotted identifier `<chipname>.<tapname>`.
- **Mandatory Parameters**:
  - `-irlen NUMBER`: Instruction register bit length.
- **Optional Parameters**:
  - `-expected-id NUMBER`: Expected 32-bit IDCODE. Can be repeated for multiple revisions.
  - `-disable` / `-enable`: Declares default link status in scan chain.
  - `-ignore-version`: Ignores bits 28..31 of IDCODE.
  - `-ignore-bypass`: Ignores invalid bypass bit behavior.
  - `-ircapture NUMBER`: Bit pattern captured upon entering `IRCAPTURE` state (default `0x01`).
  - `-irmask NUMBER`: Verification bitmask for instruction capture.
  - `-ignore-syspwrupack`: Ignores power acknowledgment bit in ARM DAP.
- **Example**:
  ```tcl
  jtag newtap stm32f4x cpu -irlen 4 -ircapture 0x1 -irmask 0xf -expected-id 0x4ba00477
  ```

### scan_chain
- **Syntax**: `scan_chain`
- **Mode**: `[Command]`
- **Description**: Displays a formatted table of all declared TAPs on the scan chain, their enabled status, IDCODEs, and IR lengths.

### jtag names
- **Syntax**: `jtag names`
- **Mode**: `[Command]`
- **Description**: Returns a Tcl list containing the dotted names of all declared TAPs.

### jtag cget
- **Syntax**: `jtag cget dotted.name (-idcode | -event event_name)`
- **Mode**: `[Command]`
- **Description**: Queries the actual IDCODE read from hardware or returns the handler script for a given TAP event.

### jtag configure
- **Syntax**: `jtag configure dotted.name -event event_name handler_body`
- **Mode**: `[Command]`
- **Description**: Assigns a Jim-Tcl script callback to a TAP event.
- **Supported Events**: `post-reset`, `setup`, `tap-enable`, `tap-disable`.

### jtag tapenable / jtag tapdisable
- **Syntax**: `jtag tapenable dotted.name` / `jtag tapdisable dotted.name`
- **Mode**: `[Command]`
- **Description**: Invokes the corresponding TAP event handler to dynamically route or unlink the TAP via a JTAG Route Controller. Returns `1` if enabled, `0` if disabled.

### jtag tapisenabled
- **Syntax**: `jtag tapisenabled dotted.name`
- **Mode**: `[Command]`
- **Description**: Returns `1` if the specified TAP is currently enabled in the scan chain, `0` if disabled.

---
## 6. ARM Debug Access Port (DAP) Declaration & Commands

### 6.1 Global DAP Commands

#### dap create
- **Syntax**: `dap create dap_name -chain-position dotted.name [options]`
- **Mode**: `[Command]`
- **Description**: Instantiates an ARM DAP object linked to the JTAG TAP `dotted.name`.
- **Options**:
  - `-adiv5`: ARM Debug Interface v5 (default).
  - `-adiv6`: ARM Debug Interface v6 (hierarchical 64-bit ROM table addresses).
  - `-ignore-syspwrupack`: Ignores sticky system powerup acknowledgment bit.
  - `-dp-id number`: Target ID for SWD DPv2 multi-drop (bits 0..27).
  - `-instance-id number`: Instance ID for SWD DPv2 multi-drop (bits 28..31).
- **Example**: `dap create stm32f4.dap -chain-position stm32f4.cpu`

#### dap names
- **Syntax**: `dap names`
- **Mode**: `[Command]`
- **Description**: Returns a list of all registered DAP objects.

#### dap info
- **Syntax**: `dap info [num|root]`
- **Mode**: `[Command]`
- **Description**: Displays the CoreSight ROM table for Access Port `num` (default: currently selected AP of current target). In ADIv6, `root` displays the root ROM table.

#### dap init
- **Syntax**: `dap init`
- **Mode**: `[Command]`
- **Description**: Initializes all registered DAP controllers.

---

### 6.2 DAP Instance Subcommands (`$dap_name`)

#### $dap_name info
- **Syntax**: `$dap_name info [num|root]`
- **Mode**: `[Command]`
- **Description**: Displays parsed ROM table and Component IDs for MEM-AP `num`.

#### $dap_name apid
- **Syntax**: `$dap_name apid [num]`
- **Mode**: `[Command]`
- **Description**: Displays identification register (`IDR`) for Access Port `num`.

#### $dap_name apreg
- **Syntax**: `$dap_name apreg ap_num reg [value]`
- **Mode**: `[Command]`
- **Description**: Reads or writes a 32-bit register `reg` (byte offset: 0, 4, 8, ... 0xfc) in Access Port `ap_num`.

#### $dap_name apsel
- **Syntax**: `$dap_name apsel [num]`
- **Mode**: `[Command]`
- **Description**: Selects the active Access Port `num` (defaults to AP 0).

#### $dap_name dpreg
- **Syntax**: `$dap_name dpreg reg [value]`
- **Mode**: `[Command]`
- **Description**: Reads or writes a Debug Port (DP) register at address `reg`. Under SWD, packed format `(dpbanksel << 4) | addr` is used.

#### $dap_name baseaddr
- **Syntax**: `$dap_name baseaddr [num]`
- **Mode**: `[Command]`
- **Description**: Displays debug base address from MEM-AP `num`.

#### $dap_name memaccess
- **Syntax**: `$dap_name memaccess [value]`
- **Mode**: `[Command]`
- **Description**: Configures number of extra TCK idle cycles for MEM-AP memory transfers (range `0..255`) for slow memory bridges.

#### $dap_name apcsw
- **Syntax**: `$dap_name apcsw [value [mask]]`
- **Mode**: `[Command]`
- **Description**: Reads or modifies Control/Status Word (`CSW`) bit patterns for MEM-AP memory accesses (e.g., setting cacheable attributes).

#### $dap_name ti_be_32_quirks
- **Syntax**: `$dap_name ti_be_32_quirks [enable]`
- **Mode**: `[Config Command]`
- **Description**: Toggles 32-bit big-endian quirks mode for Texas Instruments TMS450 / TMS570 cores.

#### $dap_name nu_npcx_quirks
- **Syntax**: `$dap_name nu_npcx_quirks [enable]`
- **Mode**: `[Config Command]`
- **Description**: Enables quirks mode for Nuvoton NPCX/NPCD microcontrollers.

---
## 7. CPU & Target Management Commands

### 7.1 Target Creation & Management

#### target create
- **Syntax**: `target create target_name type configparams...`
- **Mode**: `[Config Command]`
- **Description**: Creates a new execution debug target named `target_name`. Registers an object command `$target_name` in Jim-Tcl.
- **Parameters**:
  - `type`: Target type (e.g., `cortex_m`, `cortex_a`, `aarch64`, `riscv`, `arm7tdmi`, `xtensa`).
  - `-dap dap_name` or `-chain-position dotted.name`: Links target to DAP or TAP.
  - `-endian (big|little)`: Target byte endianness.
  - `-coreid n`: Hardware core ID in multicore architectures.
  - `-dbgbase address`: Physical memory address of debug register block.
- **Example**:
  ```tcl
  target create stm32f4x.cpu cortex_m -dap stm32f4x.dap
  ```

#### targets
- **Syntax**: `targets [name]`
- **Mode**: `[Command]`
- **Description**: Without arguments, displays a table of all created targets, their types, endianness, associated TAPs, and execution states. With `name`, switches the current default target to `name`.

#### target current
- **Syntax**: `target current`
- **Mode**: `[Command]`
- **Description**: Returns the identifier of the currently active default target.

#### target names
- **Syntax**: `target names`
- **Mode**: `[Command]`
- **Description**: Returns a Tcl list containing names of all configured targets.

#### target types
- **Syntax**: `target types`
- **Mode**: `[Command]`
- **Description**: Displays all target CPU architecture drivers compiled into OpenOCD.

#### target smp
- **Syntax**: `target smp target1 target2 ...`
- **Mode**: `[Command]`
- **Description**: Combines multiple CPU targets into a symmetric multiprocessing (SMP) cluster for synchronized breakpoints, halts, and steps.

---

### 7.2 Target Configuration Options (`$target_name configure`)
Configures parameters during target creation or via `$target_name configure`:
- `-work-area-phys address`: Physical base address of target SRAM work area.
- `-work-area-virt address`: Virtual base address of target SRAM work area when MMU is active.
- `-work-area-size size`: Size of allocated work area in bytes.
- `-work-area-backup (0|1)`: When set to `1`, saves original RAM contents before running helper algorithms and restores it afterward.
- `-endian (big|little)`: Sets CPU byte order.
- `-rtos rtos_type`: Enables RTOS thread awareness (`auto`, `none`, `FreeRTOS`, `Zephyr`, `ThreadX`, `linux`, `ChibiOS`, `embKernel`, `mqx`, `uCOS-III`, `nuttx`, `RIOT`, `hwthread`).
- `-defer-examine`: Skips target interrogation during initial startup and reset. Requires manual `arp_examine`.
- `-ap-num ap_number`: Specifies MEM-AP index (ADIv5) or base address (ADIv6).
- `-cti cti_name`: Links target to an ARM CoreSight Cross-Trigger Interface.
- `-gdb-port number`: Overrides global GDB port specifically for this target.
- `-gdb-max-connections number`: Sets maximum concurrent GDB client connections (negative means unlimited).
- `-event event_name event_body`: Registers a Jim-Tcl callback for a target lifecycle event.

---

### 7.3 Target Object Commands (`$target_name`)

- `$target_name cget queryparm`: `[Command]` Queries target configuration parameter value (e.g., `$target_name cget -work-area-phys`).
- `$target_name curstate`: `[Command]` Returns target run state: `running`, `halted`, `reset`, `debug-running`, `unknown`.
- `$target_name eventlist`: `[Command]` Displays a formatted table of all event handlers attached to this target.
- `$target_name invoke-event event_name`: `[Command]` Manually triggers execution of the handler associated with `event_name`.
- `$target_name get_reg [-force] list`: `[Command]` Retrieves register values as a Tcl dictionary. `-force` bypasses internal cache.
- `$target_name set_reg dict`: `[Command]` Sets target registers using a Tcl dictionary of name-value pairs (e.g., `$target_name set_reg {pc 0x08000100 sp 0x20001000}`).
- `$target_name read_memory address width count ['phys']`: `[Command]` Reads memory blocks into a Tcl list. Width must be 8, 16, 32, or 64 bits.
- `$target_name write_memory address width data ['phys']`: `[Command]` Writes a Tcl list of values to target memory.
- `$target_name mdd` / `mdw` / `mdh` / `mdb [phys] addr [count]`: `[Command]` Memory display commands for 64-bit, 32-bit, 16-bit, or 8-bit widths.
- `$target_name mwd` / `mww` / `mwh` / `mwb [phys] addr value [count]`: `[Command]` Memory write commands for 64-bit, 32-bit, 16-bit, or 8-bit widths.
- `$target_name arp_examine [allow-defer]`: `[Command]` Low-level target examination primitive.
- `$target_name arp_halt` / `arp_poll` / `arp_reset` / `arp_waitstate`: `[Command]` Internal execution control primitives used by OpenOCD reset procedures.

---
## 8. Target Run Control, Memory Access, & Image Operations

### 8.1 Target Execution & State Control

#### poll
- **Syntax**: `poll [on|off]`
- **Mode**: `[Command]`
- **Description**: Polls the target for current run/halt status and prints execution state, program counter, and cache status. Turns automatic background polling on or off.

#### halt
- **Syntax**: `halt [ms]`
- **Mode**: `[Command]`
- **Description**: Sends a halt request to the target CPU and waits up to `ms` milliseconds (default: 5000 ms) for the core to enter debug halt. Value `0` prevents waiting.

#### wait_halt
- **Syntax**: `wait_halt [ms]`
- **Mode**: `[Command]`
- **Description**: Waits for an already-halting target to enter debug state without sending an additional halt request.

#### resume
- **Syntax**: `resume [address]`
- **Mode**: `[Command]`
- **Description**: Resumes CPU execution at the current program counter, or at `address` if provided.

#### step
- **Syntax**: `step [address]`
- **Mode**: `[Command]`
- **Description**: Single-steps the CPU by one assembly instruction, resuming at `address` if specified.

#### reset
- **Syntax**: `reset [run|halt|init]`
- **Mode**: `[Command]`
- **Description**: Executes board reset sequence:
  - `reset run`: Resets target and allows code to execute freely.
  - `reset halt`: Resets target and halts execution at the reset vector before any instruction runs.
  - `reset init`: Resets, halts at reset vector, and executes the board-specific `reset-init` handler.

#### soft_reset_halt
- **Syntax**: `soft_reset_halt`
- **Mode**: `[Command]`
- **Description**: Soft emulation reset. Halts core and forces PC back to reset vector when hardware SRST is unavailable.

---

### 8.2 Memory Inspection & Modification Primitives

- `mdd [phys] addr [count]`: `[Command]` Reads and displays 64-bit doublewords.
- `mdw [phys] addr [count]`: `[Command]` Reads and displays 32-bit words.
- `mdh [phys] addr [count]`: `[Command]` Reads and displays 16-bit halfwords.
- `mdb [phys] addr [count]`: `[Command]` Reads and displays 8-bit bytes.
- `mwd [phys] addr value [count]`: `[Command]` Writes 64-bit doubleword to memory.
- `mww [phys] addr value [count]`: `[Command]` Writes 32-bit word to memory.
- `mwh [phys] addr value [count]`: `[Command]` Writes 16-bit halfword to memory.
- `mwb [phys] addr value [count]`: `[Command]` Writes 8-bit byte to memory.

---

### 8.3 CPU Register Commands

#### reg
- **Syntax**: `reg [(number|name) [(value|'force')]]`
- **Mode**: `[Command]`
- **Description**: With no arguments, prints all CPU registers, their sizes, cache validity, and dirty status. With a register name or number, reads the value. With a value argument, updates the register (writes are flushed to hardware upon CPU resume or step). `'force'` bypasses internal register caching.

---

### 8.4 Binary & Hex Image Loading/Dumping

#### load_image
- **Syntax**: `load_image filename address [[bin|ihex|elf|s19] min_addr max_length]`
- **Mode**: `[Command]`
- **Description**: Loads an image file into target memory starting at `address`. Supports raw binary (`bin`), Intel hex (`ihex`), ELF (`elf`), and Motorola S-records (`s19`).

#### dump_image
- **Syntax**: `dump_image filename address size`
- **Mode**: `[Command]`
- **Description**: Dumps `size` bytes from target memory starting at `address` into a local binary file.

#### fast_load_image
- **Syntax**: `fast_load_image filename address [bin|ihex|elf|s19]`
- **Mode**: `[Command]`
- **Description**: Preloads an image into OpenOCD host memory cache to accelerate multiple repeated debugging cycles.

#### fast_load
- **Syntax**: `fast_load`
- **Mode**: `[Command]`
- **Description**: Flushes preloaded image from host memory into target memory.

#### test_image
- **Syntax**: `test_image filename [address [bin|ihex|elf]]`
- **Mode**: `[Command]`
- **Description**: Displays section headers, memory addresses, and sizes as if the file were loaded into memory.

#### verify_image
- **Syntax**: `verify_image filename address [bin|ihex|elf]`
- **Mode**: `[Command]`
- **Description**: Verifies target memory contents against `filename` using CRC32 checksums, falling back to byte comparison on mismatch.

#### verify_image_checksum
- **Syntax**: `verify_image_checksum filename address [bin|ihex|elf]`
- **Mode**: `[Command]`
- **Description**: Verifies target memory against `filename` using target-assisted CRC checksum algorithms only.

---

### 8.5 Breakpoints & Watchpoints

#### bp
- **Syntax**: `bp [address len [hw]]`
- **Mode**: `[Command]`
- **Description**: Lists active breakpoints, or sets a breakpoint at `address` for `len` bytes. If `hw` is specified, forces allocation of a hardware comparator.

#### rbp
- **Syntax**: `rbp all | address`
- **Mode**: `[Command]`
- **Description**: Removes breakpoint at `address` or removes all active breakpoints.

#### wp
- **Syntax**: `wp [address len [(r|w|a) [value [mask]]]]`
- **Mode**: `[Command]`
- **Description**: Lists active watchpoints or sets a data watchpoint at `address` for `len` bytes. Triggers on read (`r`), write (`w`), or access (`a`). Supports value and bitmask matching.

#### rwp
- **Syntax**: `rwp address`
- **Mode**: `[Command]`
- **Description**: Removes data watchpoint set on `address`.

---

### 8.6 Real Time Transfer (RTT)
High-speed bidirectional telemetry over standard JTAG/SWD:

- `rtt setup address size ID`: `[Command]` Configures RTT search block in target RAM starting at `address` for `size` bytes, looking for string `ID` (e.g., `"SEGGER RTT"`).
- `rtt start`: `[Command]` Initiates RTT polling engine.
- `rtt stop`: `[Command]` Halts RTT polling.
- `rtt polling_interval [interval]`: `[Command]` Displays or sets RTT up-channel check interval in milliseconds.
- `rtt channels`: `[Command]` Lists all discovered RTT channels and buffer sizes.
- `rtt channellist`: `[Command]` Returns channel properties as a Tcl list.
- `rtt server start port channel`: `[Command]` Starts a TCP server on host `port` forwarding stream data for RTT `channel`.
- `rtt server stop port`: `[Command]` Terminates TCP server on `port`.

---

### 8.7 Profiling & Utility Commands

- `profile seconds filename [start end]`: `[Command]` Stochastic PC sampling for `seconds` duration. Outputs gmon.out format profiling data.
- `version`: `[Command]` Returns OpenOCD software release version string.
- `virt2phys virtual_address`: `[Command]` Queries target MMU to resolve physical address corresponding to `virtual_address`.
- `add_help_text 'command_name' 'help-string'`: `[Command]` Registers custom documentation for a command.
- `add_usage_text 'command_name' 'usage-string'`: `[Command]` Registers syntax usage text for a command.

---
## 9. Flash Subsystem & Driver-Specific Commands

### 9.1 General NOR Flash Commands

#### flash bank
- **Syntax**: `flash bank name driver base size chip_width bus_width target [driver_options]`
- **Mode**: `[Config Command]`
- **Description**: Registers a persistent flash bank covering memory from `base` to `base + size - 1`. Links the bank to driver `driver` and execution target `target`.
- **Example**:
  ```tcl
  flash bank $_FLASHNAME stm32f4x 0x08000000 0 0 0 $_TARGETNAME
  ```

#### flash banks
- **Syntax**: `flash banks`
- **Mode**: `[Command]`
- **Description**: Prints a formatted summary of all declared flash banks, base addresses, sizes, and driver types.

#### flash list
- **Syntax**: `flash list`
- **Mode**: `[Command]`
- **Description**: Returns a structured Tcl list of associative arrays describing declared flash devices.

#### flash probe
- **Syntax**: `flash probe num`
- **Mode**: `[Command]`
- **Description**: Interrogates flash controller hardware to identify chip geometry, sector boundaries, and capacity.

#### flash erase_sector
- **Syntax**: `flash erase_sector num first last`
- **Mode**: `[Command]`
- **Description**: Erases sectors in bank `num` from index `first` to `last` (inclusive). Using `last` as the end index erases to bank conclusion.

#### flash erase_address
- **Syntax**: `flash erase_address [pad] [unlock] address length`
- **Mode**: `[Command]`
- **Description**: Erases flash sectors spanning `address` to `address + length - 1`. `pad` extends boundaries to cover whole sectors. `unlock` removes sector protection before erasing.

#### flash write_bank
- **Syntax**: `flash write_bank num filename [offset]`
- **Mode**: `[Command]`
- **Description**: Programs raw binary file `filename` to flash bank `num` starting at `offset`.

#### flash read_bank
- **Syntax**: `flash read_bank num filename [offset [length]]`
- **Mode**: `[Command]`
- **Description**: Dumps `length` bytes from bank `num` at `offset` into binary file `filename`.

#### flash verify_bank
- **Syntax**: `flash verify_bank num filename [offset]`
- **Mode**: `[Command]`
- **Description**: Verifies bank contents against binary file `filename`.

#### flash write_image
- **Syntax**: `flash write_image [erase] [unlock] filename [offset] [type]`
- **Mode**: `[Command]`
- **Description**: Automatically programs loadable sections of an image file (`elf`, `hex`, `s19`, `bin`) into mapped flash banks. `erase` erases affected sectors beforehand; `unlock` unprotects flash.

#### flash verify_image
- **Syntax**: `flash verify_image filename [offset] [type]`
- **Mode**: `[Command]`
- **Description**: Verifies mapped flash banks against image `filename`.

#### flash erase_check
- **Syntax**: `flash erase_check num`
- **Mode**: `[Command]`
- **Description**: Verifies whether sectors in bank `num` are in erased state (`0xFF`).

#### flash info
- **Syntax**: `flash info num [sectors]`
- **Mode**: `[Command]`
- **Description**: Displays hardware protection status, lock blocks, and sector geometry for bank `num`.

#### flash protect
- **Syntax**: `flash protect num first last (on|off)`
- **Mode**: `[Command]`
- **Description**: Enables (`on`) or disables (`off`) write protection for blocks in bank `num`.

#### flash padded_value
- **Syntax**: `flash padded_value num value`
- **Mode**: `[Command]`
- **Description**: Sets fill byte value for padding sector alignments (default `0xff`).

#### flash filld / fillw / fillh / fillb
- **Syntax**: `flash filld|fillw|fillh|fillb address pattern length`
- **Mode**: `[Command]`
- **Description**: Fills flash blocks with repeated 64-bit, 32-bit, 16-bit, or 8-bit pattern without prior erase.

#### flash mdd / mdw / mdh / mdb
- **Syntax**: `flash mdd|mdw|mdh|mdb addr [count]`
- **Mode**: `[Command]`
- **Description**: Reads flash memory through driver access methods, allowing inspection of banks not mapped directly into CPU address space.

#### program
- **Syntax**: `program filename [preverify] [verify] [reset] [exit] [offset]`
- **Mode**: `[Command]`
- **Description**: High-level monolithic Jim-Tcl helper procedure that executes `init`, `reset init`, `flash write_image erase`, optional pre-verify/verify, reset, and shutdown.

---

### 9.2 External NOR Flash Drivers
- `cfi`: `[Flash Driver]` Common Flash Interface driver for parallel NOR flash chips on system bus. Options: `jedec_probe`, `x16_as_x8`, `bus_swap`, `data_swap`.
- `jtagspi`: `[Flash Driver]` Direct SPI flash programming on FPGAs via proxy bitstreams.
  - `jtagspi set bank_id name total_size page_size read_cmd [pprg_cmd mass_erase_cmd sector_size sector_erase_cmd]`: `[Command]` Defines custom SPI flash timing and command parameters.
  - `jtagspi cmd bank_id resp_num cmd_byte ...`: `[Command]` Sends arbitrary SPI command bytes over JTAG.
  - `jtagspi always_4byte bank_id [on|off]`: `[Command]` Forces 4-byte address mode.
- `xcf`: `[Flash Driver]` Xilinx Platform Flash PROMs.
  - `xcf ccb <bank_id> [external|internal] [serial|parallel] [slave|master] [40|20]`: `[Command]` Configures Customer Configuration Bits.
  - `xcf configure <bank_id>`: `[Command]` Triggers FPGA configuration load.
- `stmqspi`: `[Flash Driver]` STMicroelectronics QuadSPI/OctoSPI controllers.
  - `stmqspi mass_erase bank_id`: `[Command]` Clears sector protection and executes mass erase.
  - `stmqspi set bank_id name total_size page_size read_cmd ...`: `[Command]` Configures custom chip geometry.
  - `stmqspi cmd bank_id resp_num cmd_byte ...`: `[Command]` Sends custom QSPI/OSPI commands.
- `lpcspifi`: `[Flash Driver]` NXP LPC18xx/LPC43xx SPI Flash Interface controller.
- `stmsmi`: `[Flash Driver]` ST STR75x / SPEAr Serial Memory Interface controller.
- `mrvlqspi`: `[Flash Driver]` Marvell Wireless Microcontroller QSPI controller.
- `ath79`: `[Flash Driver]` Atheros ATH79 SPI flash controller (supports chipselects `cs0`, `cs1`, `cs2`).
- `fespi`: `[Flash Driver]` SiFive Freedom E SPI controller (HiFive boards).
- `virtual`: `[Flash Driver]` Maps a virtual address alias to an underlying master physical flash bank.

---

### 9.3 Microcontroller Internal Flash Drivers & Controller Commands

#### 9.3.1 Microchip / Atmel
- `at91samd`: `[Flash Driver]` ATSAM D0x/D1x/D2x/SAMR/SAML/SAMC (Cortex-M0+).
  - `at91samd chip-erase`: `[Command]` Erases entire chip via Device Service Unit (DSU) even if secured.
  - `at91samd set-security`: `[Command]` Asserts Security Bit (SSB) to lock chip.
  - `at91samd eeprom [size]`: `[Command]` Configures emulated EEPROM size in User Row.
  - `at91samd bootloader [size]`: `[Command]` Configures BOOTPROT bootloader protection size.
  - `at91samd nvmuserrow [value [changemask]]`: `[Command]` Reads or writes 64-bit NVM user row fuses.
  - `at91samd dsu_reset_deassert`: `[Command]` Releases internal DSU reset for vector catch.
- `atsame5`: `[Flash Driver]` SAM E51/E53/E54 and D51 (Cortex-M4).
  - `atsame5 chip-erase` / `bootloader` / `userpage` / `dsu_reset_deassert`: `[Command]` User page fuses and bootloader protection.
- `at91sam3` / `at91sam4` / `at91sam4l`: `[Flash Driver]` SAM3/SAM4 (Cortex-M3/M4).
  - `at91sam3 gpnvm [show|set|clear] [number]`: `[Command]` Reads or toggles General Purpose NVM bits.
  - `at91sam3 info`: `[Command]` Decodes CHIPID and clock registers.
  - `at91sam3 slowclk [value]`: `[Command]` Configures slow clock frequency for timing calculations.
  - `at91sam4l smap_reset_deassert`: `[Command]` Releases SMAP reset.
- `atsamv`: `[Flash Driver]` SAM V7x, S70, E70 (Cortex-M7).
  - `atsamv gpnvm [show|set|clr] [number]`: `[Command]` Controls GPNVM bits (e.g., TCM configuration, boot source).
- `at91sam7`: `[Flash Driver]` AT91SAM7 (ARM7TDMI).
  - `at91sam7 gpnvm bitnum (set|clear)`: `[Command]` Brownout detection and boot select bits.
- `aduc702x`: `[Flash Driver]` Analog Devices ADuC7019..ADuC7028 microcontrollers.

#### 9.3.2 STMicroelectronics
- `stm32f1x`: `[Flash Driver]` STM32F0, F1, F3, and GD32F1/F3/E2/RISC-V derivatives.
  - `stm32f1x lock num` / `unlock num`: `[Command]` Readout protection control (unlock triggers mass erase).
  - `stm32f1x mass_erase num`: `[Command]` Mass erases entire device.
  - `stm32f1x options_read num`: `[Command]` Reads option bytes.
  - `stm32f1x options_write num (SWWDG|HWWDG) (RSTSTNDBY|NORSTSTNDBY) (RSTSTOP|NORSTSTOP) (USEROPT user_data)`: `[Command]` Programs hardware watchdog and standby option bytes.
  - `stm32f1x options_load num`: `[Command]` Forces option byte reload reset.
- `stm32f2x`: `[Flash Driver]` STM32F2, STM32F4, STM32F7.
  - `stm32f2x lock` / `unlock` / `mass_erase`: `[Command]` Security control and bulk erasure.
  - `stm32f2x otp num (enable|disable|show)`: `[Command]` Enables OTP block programming.
  - `stm32f2x options_read` / `options_write`: `[Command]` Manages FLASH_OPTCR registers.
  - `stm32f2x optcr2_write num optcr2`: `[Command]` Programs PCROP read protection on OPTCR2.
- `stm32h7x`: `[Flash Driver]` STM32H7 dual-bank Cortex-M7 devices.
  - `stm32h7x lock` / `unlock` / `mass_erase`: `[Command]` Security management.
  - `stm32h7x option_read num reg_offset`: `[Command]` Reads raw option register.
  - `stm32h7x option_write num reg_offset value [reg_mask]`: `[Command]` Modifies option bytes (e.g., bank swap).
- `stm32lx`: `[Flash Driver]` STM32L0 and STM32L1 ultra-low-power MCUs.
  - `stm32lx lock` / `unlock` / `mass_erase`: `[Command]` RDP level management and EEPROM wipe.
- `stm32l4x`: `[Flash Driver]` STM32 G0, G4, L4, L4+, L5, U5, WB, WL.
  - `stm32l4x lock` / `unlock` / `mass_erase`: `[Command]` Security control.
  - `stm32l4x option_read` / `option_write`: `[Command]` Manages `FLASH_OPTR` registers.
  - `stm32l4x option_load num`: `[Command]` Triggers system reset to reload option bytes.
  - `stm32l4x wrp_info num [bank1|bank2]`: `[Command]` Displays write-protected areas.
  - `stm32l4x trustzone num [enable|disable]`: `[Command]` Toggles Global TrustZone Security (`TZEN`).
  - `stm32l4x otp num (enable|disable|show)`: `[Command]` Controls OTP sector programming.
- `bluenrg-x`: `[Flash Driver]` ST BlueNRG-1, BlueNRG-2, BlueNRG-LP/LPS BLE SoCs.
- `str7x`: `[Flash Driver]` STR71x, STR73x, STR75x.
  - `str7x disable_jtag bank`: `[Command]` Engages readout protection.
- `str9x`: `[Flash Driver]` STR91x (ARM966E).
  - `str9x flash_config num bbsr nbbsr bbadr nbbadr`: `[Command]` Sets boot bank size and address mappings.
- `str9xpec`: `[Flash Driver]` Direct programming of STR9 via dedicated IEEE 1532 ISC TAP.
  - `str9xpec enable_turbo num` / `disable_turbo num`: `[Command]` Unlinks CPU from chain to talk directly to flash controller.
  - `str9xpec lock num` / `unlock num`: `[Command]` Device locking/unlocking.
  - `str9xpec options_read` / `options_write`: `[Command]` Reads or writes boot configuration option bytes.
  - `str9xpec options_cmap` / `options_lvdsel` / `options_lvdthd` / `options_lvdwarn`: `[Command]` Voltage threshold and warning controls.
  - `str9xpec part_id num`: `[Command]` Queries part ID code.

#### 9.3.3 NXP / Freescale
- `kinetis`: `[Flash Driver]` NXP Kinetis Kx, KLx, KVx, KE1x (Cortex-M0+/M4).
  - `kinetis create_banks`: `[Config Command]` Dynamically creates flash banks based on probed hardware layout.
  - `kinetis fcf_source [protection|write]`: `[Command]` Chooses whether Flash Configuration Field is synthesized from protection bits or written from image.
  - `kinetis fopt [num]`: `[Command]` Sets FOPT byte value in Flash Configuration Field.
  - `kinetis mdm check_security`: `[Command]` Queries MDM-AP security lock status.
  - `kinetis mdm halt`: `[Command]` Asserts halt over MDM-AP to break watchdog reboot loops.
  - `kinetis mdm mass_erase`: `[Command]` Complete chip erase via MDM-AP, removing security bit.
  - `kinetis mdm reset`: `[Command]` Pulses board RESET pin via MDM-AP.
  - `kinetis nvm_partition [info | dataflash ... | eebkp ...]`: `[Command]` Configures FlexNVM and FlexRAM partition sizes.
  - `kinetis disable_wdog`: `[Command]` Disables watchdog timer to stabilize debug sessions.
- `kinetis_ke`: `[Flash Driver]` Kinetis KE0x and KEAx automotive MCUs.
  - `kinetis_ke mdm check_security` / `mass_erase` / `disable_wdog`: `[Command]` MDM-AP controls.
- `lpc2000`: `[Flash Driver]` NXP LPC800, LPC11xx, LPC13xx, LPC15xx, LPC17xx, LPC18xx, LPC2000, LPC4000, LPC54100.
  - `lpc2000 part_id bank`: `[Command]` Reads 32-bit internal part identification register.
- `lpc288x`: `[Flash Driver]` NXP LPC2888 microcontrollers.
- `lpc2900`: `[Flash Driver]` NXP LPC29xx ARM966E microcontrollers.
  - `lpc2900 signature bank`: `[Command]` Calculates 128-bit hardware hash signature of programmed flash.
  - `lpc2900 read_custom bank filename`: `[Command]` Dumps 912 bytes of customer index sector.
  - `lpc2900 password bank password`: `[Command]` Unlocks protected operations with password `"I_know_what_I_am_doing"`.
  - `lpc2900 write_custom bank filename type`: `[Command]` Writes 912-byte customer data block.
  - `lpc2900 secure_sector bank first last`: `[Command]` Irreversibly locks sectors against erase/write.
  - `lpc2900 secure_jtag bank`: `[Command]` Irreversibly disables JTAG port.

#### 9.3.4 Cypress
- `psoc4`: `[Flash Driver]` PSoC 41xx/42xx.
  - `psoc4 flash_autoerase num (on|off)`: `[Command]` Controls single-step erase-and-program mode.
  - `psoc4 mass_erase num`: `[Command]` Complete flash wipe.
- `psoc5lp`: `[Flash Driver]` PSoC 5LP (Cortex-M3).
  - `psoc5lp mass_erase`: `[Command]` Erases flash, ECC rows, and protection latches.
- `psoc5lp_eeprom`: `[Flash Driver]` Internal EEPROM driver.
- `psoc5lp_nvl`: `[Flash Driver]` Non-Volatile Latches driver.
- `psoc6`: `[Flash Driver]` PSoC 6 dual-core (CM0+ and CM4) microcontrollers.
  - `psoc6 reset_halt`: `[Command]` Simulates Vector Catch by breaking at application entry point and asserting `SYSRESETREQ` or `VECTRESET`.
  - `psoc6 mass_erase num`: `[Command]` Erases Main and Work flash regions.

#### 9.3.5 Texas Instruments
- `cc26xx`: `[Flash Driver]` SimpleLink CC13xx and CC26xx wireless MCUs.
- `cc3220sf`: `[Flash Driver]` SimpleLink CC3220SF Wi-Fi MCU with 1 MB internal flash.
- `stellaris`: `[Flash Driver]` Stellaris LM3S, LM4x, and Tiva C microcontrollers.
  - `stellaris recover`: `[Command]` Executes "Locked Device Recovery" algorithm to recover bricked chips.
- `msp432`: `[Flash Driver]` SimpleLink MSP432 microcontrollers.
  - `msp432 mass_erase bank_id [main|all]`: `[Command]` Mass erases main and info flash banks.
  - `msp432 bsl bank_id [unlock|lock]`: `[Command]` Locks or unlocks Bootstrap Loader memory region.
- `tms470`: `[Flash Driver]` TMS470 ARM7TDMI chips.
  - `tms470 flash_keyset key0 key1 key2 key3`: `[Command]` Loads authorization keys.
  - `tms470 osc_megahertz clock_mhz`: `[Command]` Sets crystal frequency.
  - `tms470 plldis (0|1)`: `[Command]` Enables/disables PLL for flash timing.

#### 9.3.6 Nordic Semiconductor
- `nrf5`: `[Flash Driver]` nRF51, nRF52832, nRF52833, nRF52840.
  - `nrf5 mass_erase`: `[Command]` Erases code memory and UICR registers.
  - `nrf5 info`: `[Command]` Decodes Factory (FICR) and User (UICR) configuration registers.

#### 9.3.7 Silicon Labs
- `efm32`: `[Flash Driver]` EFM32 and EFR32 Gecko microcontrollers.
  - `efm32 debuglock num`: `[Command]` Disables debug interface via Debug Lock Word.
- `sim3x`: `[Flash Driver]` SiM3x family microcontrollers.
  - `sim3x mass_erase`: `[Command]` Erases flash to unlock device over SWD.
  - `sim3x lock`: `[Command]` Locks flash interface.

#### 9.3.8 Raspberry Pi & Onsemi
- `rp2040`: `[Flash Driver]` Raspberry Pi RP2040 dual Cortex-M0+ SoC with external QSPI flash.
- `rsl10`: `[Flash Driver]` Onsemi RSL10 Bluetooth 5 radio MCU.
  - `rsl10 lock key1 key2 key3 key4`: `[Command]` Locks debug interface.
  - `rsl10 unlock key1 key2 key3 key4`: `[Command]` Unlocks debug interface over DAP registers.
  - `rsl10 mass_erase`: `[Command]` Erases all unprotected sectors.

#### 9.3.9 Fujitsu / Spansion
- `fm3`: `[Flash Driver]` Fujitsu FM3 Cortex-M3 family.
- `fm4`: `[Flash Driver]` Spansion FM4 Cortex-M4 family.

#### 9.3.10 Infineon
- `xmc1xxx`: `[Flash Driver]` Infineon XMC1000 family (Cortex-M0).
- `xmc4xxx`: `[Flash Driver]` Infineon XMC4000 family (Cortex-M4).
  - `xmc4xxx flash_password bank_id passwd1 passwd2`: `[Command]` Sets protection passwords.
  - `xmc4xxx flash_unprotect bank_id user_level[0-1]`: `[Command]` Removes write protection.

#### 9.3.11 Other Vendors
- `ambiqmicro`: `[Flash Driver]` Ambiq Micro Apollo Cortex-M4 SoCs.
  - `ambiqmicro mass_erase <bank>` / `page_erase` / `program_otp`: `[Command]` Erase and OTP programming.
- `mdr`: `[Flash Driver]` Milandr Cortex-M microcontrollers.
- `niietcm4`: `[Flash Driver]` NIIET Cortex-M4 microcontrollers.
  - `niietcm4 uflash_read_byte` / `uflash_write_byte`: `[Command]` Userflash byte access.
  - `niietcm4 uflash_full_erase` / `uflash_erase`: `[Command]` Userflash erasure.
  - `niietcm4 uflash_protect_check` / `uflash_protect`: `[Command]` Sector protection.
  - `niietcm4 bflash_info_remap ('on'|'off')`: `[Command]` Remaps Bootflash info sector.
  - `niietcm4 extmem_cfg`: `[Command]` Sets up external boot memory pins.
  - `niietcm4 service_mode_erase`: `[Command]` Emergency mass wipe of all flash.
  - `niietcm4 driver_info`: `[Command]` Displays driver diagnostics.
- `npcx`: `[Flash Driver]` Nuvoton NPCX embedded controllers.
- `pic32mx`: `[Flash Driver]` Microchip PIC32MX (MIPS 4K).
  - `pic32mx pgm_word address value bank`: `[Command]` Programs single 32-bit word.
  - `pic32mx unlock bank`: `[Command]` Removes code protection via mass erase.
- `swm050`: `[Flash Driver]` Synwit SWM050 microcontrollers.
  - `swm050 mass_erase bank_id`: `[Command]` Erases flash bank.
- `w600`: `[Flash Driver]` WinnerMicro W600 Wi-Fi Cortex-M3 SoC.
- `esirisc`: `[Flash Driver]` EnSilica eSi-RISC on-chip flash.
  - `esirisc flash mass_erase` / `ref_erase`: `[Command]` Erases data flash and reference cells.
- `ocl`: `[Flash Driver]` On-Chip Flash Loader DCC protocol driver.
- `avr`: `[Flash Driver]` Atmel 8-bit AVR microcontrollers (preliminary).

---
## 10. NAND Flash Commands & Drivers

### 10.1 General NAND Commands

#### nand device
- **Syntax**: `nand device name driver target [configparams...]`
- **Mode**: `[Config Command]`
- **Description**: Registers a NAND flash device named `name` controlled by driver `driver` via target `target`.
- **Example**: `nand device mx35.nand mxc imx35.cpu mx35 hwecc biswap`

#### nand list
- **Syntax**: `nand list`
- **Mode**: `[Command]`
- **Description**: Displays summary of all registered NAND devices, page sizes, block counts, and bus widths.

#### nand probe
- **Syntax**: `nand probe num`
- **Mode**: `[Command]`
- **Description**: Queries the NAND controller to read device ID and populate page/block geometry.

#### nand dump
- **Syntax**: `nand dump num filename offset length [oob_option]`
- **Mode**: `[Command]`
- **Description**: Dumps pages from device `num` to `filename`. `oob_option` can be `no_oob` (default), `oob_raw` (interleaved data and spare bytes), or `oob_only`.

#### nand erase
- **Syntax**: `nand erase num [offset length]`
- **Mode**: `[Command]`
- **Description**: Erases NAND blocks. Must align with block boundaries.

#### nand write
- **Syntax**: `nand write num filename offset [option...]`
- **Mode**: `[Command]`
- **Description**: Writes binary image `filename` to device `num`. Options: `oob_raw`, `oob_only`, `oob_softecc` (1-bit software ECC), `oob_softecc_kw` (Marvell Kirkwood 4-bit ECC).

#### nand verify
- **Syntax**: `nand verify num filename offset [option...]`
- **Mode**: `[Command]`
- **Description**: Verifies written pages and OOB metadata against source file.

#### nand check_bad_blocks
- **Syntax**: `nand check_bad_blocks num [offset length]`
- **Mode**: `[Command]`
- **Description**: Scans flash pages for manufacturer bad block markers. Requires `nand raw_access enable`.

#### nand info
- **Syntax**: `nand info num`
- **Mode**: `[Command]`
- **Description**: Prints status summary and bad block map for device `num`.

#### nand raw_access
- **Syntax**: `nand raw_access num (enable|disable)`
- **Mode**: `[Command]`
- **Description**: Disables hardware ECC generation to perform raw read/write access to flash cells.

---

### 10.2 NAND Controller Drivers
- `at91sam9`: `[NAND Driver]` Atmel AT91SAM9 hardware ECC controller.
  - `at91sam9 cle num addr_line`: `[Config Command]` Configures Command Latch Enable address pin.
  - `at91sam9 ale num addr_line`: `[Config Command]` Configures Address Latch Enable pin.
  - `at91sam9 rdy_busy num pio_base_addr pin`: `[Config Command]` Configures Ready/Busy pin.
  - `at91sam9 ce num pio_base_addr pin`: `[Config Command]` Configures Chip Enable pin.
- `davinci`: `[NAND Driver]` TI DaVinci AEMIF controller (supports `hwecc1`, `hwecc4`, `hwecc4_infix`).
- `lpc3180`: `[NAND Driver]` NXP LPC3180 NAND controller.
  - `lpc3180 select num [mlc|slc]`: `[Command]` Toggles Multi-Level Cell (hardware ECC) vs. Single-Level Cell mode.
- `mx3` / `mxc`: `[NAND Driver]` Freescale i.MX27/31/35 NAND controllers.
  - `mxc biswap bank_num [enable|disable]`: `[Command]` Swaps bad block marker bytes between main and spare areas.
- `orion`: `[NAND Driver]` Marvell Orion / Kirkwood NAND controller.
- `s3c2410`, `s3c2412`, `s3c2440`, `s3c2443`, `s3c6400`: `[NAND Driver]` Samsung S3C NAND controllers.

---
## 11. PLD / FPGA Configuration Commands

### pld device
- **Syntax**: `pld device driver_name tap_name [driver_options]`
- **Mode**: `[Config Command]`
- **Description**: Declares a Programmable Logic Device (PLD/FPGA) associated with TAP `tap_name`.

### pld devices
- **Syntax**: `pld devices`
- **Mode**: `[Command]`
- **Description**: Lists all declared PLD/FPGA devices and their index numbers.

### pld load
- **Syntax**: `pld load num filename`
- **Mode**: `[Command]`
- **Description**: Streams hardware bitstream file `filename` into PLD device `num`.

### virtex2
- **Syntax**: `virtex2 [no_jstart]`
- **Mode**: `[FPGA Driver]`
- **Description**: Driver for Xilinx Virtex-II, Series-3, Series-6, Series-7, and Zynq-7000 FPGAs implementing IEEE 1532 In-System Configuration. If `no_jstart` is non-zero, disables `JSTART` instruction (required for Series-7).
- `virtex2 read_stat num`: `[Command]` Reads and decodes 32-bit FPGA status register (`STAT`).

---
## 12. Architecture & Core-Specific Commands

### 12.1 ARM Hardware Tracing (ETM, ETB, Trace Port Drivers)
- `etm config target width mode clocking driver`: `[Config Command]` Links target ETM to trace port driver. Width: 4, 8, 16. Mode: normal, multiplexed, demultiplexed. Clocking: half, full.
- `etm info`: `[Command]` Queries ETM configuration and hardware capability registers.
- `etm status`: `[Command]` Returns whether ETM is collecting, triggered, or overflowed.
- `etm tracemode [type context_id_bits cycle_accurate branch_output]`: `[Command]` Configures trace data capture: `type` (`none`, `data`, `address`, `all`), context IDs (`0`, `8`, `16`, `32`), cycle-accurate timing, branch broadcast.
- `etm trigger_debug (enable|disable)`: `[Command]` Causes ETM trigger condition to halt CPU into debug state.
- `etm start` / `etm stop`: `[Command]` Starts or halts trace collection.
- `etm dump filename` / `etm load filename`: `[Command]` Saves or loads captured trace packets to/from disk.
- `etm analyze`: `[Command]` Decodes instruction trace records in OpenOCD memory.
- `etm image filename [base_address] [type]`: `[Command]` Associates binary executable image for trace disassembly.
- `etm_dummy config target`: `[Config Command]` Links ETM to dummy driver.
- `etb config target etb_tap`: `[Config Command]` Links ETM to on-chip Embedded Trace Buffer SRAM.
- `etb trigger_percent [percent]`: `[Command]` Configures pre/post trigger trace buffer split (2% to 100%).

---

### 12.2 ARM CoreSight Cross-Trigger Interface (CTI)
- `cti create cti_name -dap dap_name -ap-num apn -baseaddr base_address`: `[Command]` Instantiates CTI control object `$cti_name`.
- `cti names`: `[Command]` Lists all created CTI objects.
- `$cti_name enable on|off`: `[Command]` Enables/disables CTI.
- `$cti_name dump`: `[Command]` Dumps CTI registers.
- `$cti_name write reg_name value` / `read reg_name`: `[Command]` Accesses CTI registers.
- `$cti_name ack event`: `[Command]` Acknowledges trigger event.
- `$cti_name channel channel_number operation`: `[Command]` Channel operations (`gate`, `ungate`, `set`, `clear`, `pulse`).
- `$cti_name testmode on|off`: `[Command]` Toggles CTI integration test mode.

---

### 12.3 Generic ARM Commands
- `arm core_state [arm|thumb]`: `[Command]` Displays or switches execution mode between 32-bit ARM and 16/32-bit Thumb.
- `arm disassemble address [count [thumb]]`: `[Command]` Disassembles instructions at `address`.
- `arm mcr pX op1 CRn CRm op2 value`: `[Command]` Writes coprocessor register via MCR instruction.
- `arm mrc pX op1 CRn CRm op2`: `[Command]` Reads coprocessor register via MRC instruction.
- `arm reg`: `[Command]` Displays all banked ARM core registers across all execution modes (User, FIQ, IRQ, Supervisor, Abort, Undefined).
- `arm semihosting [enable|disable]`: `[Command]` Toggles ARM semihosting trap handler.
- `arm semihosting_redirect (disable | tcp <port> [debug|stdio|all])`: `[Command]` Redirects semihosting stdio to a TCP port.
- `arm semihosting_cmdline argv0 argv1 ...`: `[Command]` Passes command-line arguments to target semihosted application.
- `arm semihosting_fileio [enable|disable]`: `[Command]` Routes semihosting system calls through GDB File-I/O remote protocol.
- `arm semihosting_resexit [enable|disable]`: `[Command]` Allows `SYS_EXIT` semihosting call to return without halting debugger.
- `arm semihosting_basedir [dir]`: `[Command]` Sets root directory for host file access.
- `arm semihosting_read_user_param`: `[Command]` Extracts user parameter string passed with semihosting calls `0x100..0x107`.

---

### 12.4 ARMv4 and ARMv5 Architecture Specific Commands
- `arm7_9 dbgrq [enable|disable]`: `[Command]` Uses EmbeddedICE `DBGRQ` signal instead of hardware breakpoints for halt.
- `arm7_9 dcc_downloads [enable|disable]`: `[Command]` Uses DCC coprocessor for fast memory downloads.
- `arm7_9 fast_memory_access [enable|disable]`: `[Command]` Bypasses memory write completion checks for high throughput.
- `arm9 vector_catch [all|none|list]`: `[Command]` Hardware interception of exceptions: `reset`, `undef`, `swi`, `pabt`, `dabt`, `irq`, `fiq`.
- `arm920t cache_info` / `cp15 regnum [value]` / `read_cache filename` / `read_mmu filename`: `[Command]` Cache and MMU inspection for ARM920T.
- `arm926ejs cache_info`: `[Command]` Cache info for ARM926EJ-S / Feroceon.
- `arm966e cp15 regnum [value]`: `[Command]` CP15 access for ARM966E.
- `xscale vector_table [(low|high) index value]`: `[Command]` Configures mini-IC exception vector table for Intel XScale cores.
- `xscale debug_handler target address`: `[Command]` Address of XScale target-resident debug handler.
- `xscale cache_clean_address address` / `cache_info` / `cp15 regnum [value]`: `[Command]` Cache controls.
- `xscale dcache [enable|disable]` / `icache [enable|disable]` / `mmu [enable|disable]`: `[Command]` Memory subsystem toggles.
- `xscale vector_catch [mask]`: `[Command]` Vector catch mask for XScale DCSR.
- `xscale trace_buffer [enable|disable [fill [n] | wrap]]` / `dump_trace filename` / `analyze_trace` / `trace_image`: `[Command]` XScale trace buffer operations.

---

### 12.5 ARMv6 Architecture (ARM11)
- `arm11 memwrite burst [enable|disable]`: `[Command]` Enables burst memory writes without waiting for individual word acknowledgments.
- `arm11 memwrite error_fatal [enable|disable]`: `[Command]` Aborts burst write transfer immediately upon bus error.
- `arm11 step_irq_enable [enable|disable]`: `[Command]` Permits IRQs to execute while single-stepping.
- `arm11 vcr [value]`: `[Command]` Configures Vector Catch Register (CP14 register 7).

---

### 12.6 ARMv7-A and ARMv7-R Architectures
- `cortex_a cache_info`: `[Command]` Displays L1/L2 cache topology.
- `cortex_a dacrfixup [on|off]`: `[Command]` Bypasses MMU permission faults for breakpoints by forcing CP15 DACR to all-manager mode.
- `cortex_a dbginit`: `[Command]` Clears OS Lock and powerdown bits in Cortex-A debug registers.
- `cortex_a smp [on|off]` / `cortex_a smp_gdb [core_id]`: `[Command]` Toggles SMP mode and switches active core presented to GDB.
- `cortex_a maskisr [on|off]`: `[Command]` Masks interrupts during instruction stepping.
- `cortex_a mmu dump [0|1|addr address [num_entries]]`: `[Command]` Decodes page tables from TTB0, TTB1, or physical address.
- `cache_config l2x [base way]`: `[Command]` Configures Level 2 cache controller.
- `cortex_r4 dbginit` / `maskisr`: `[Command]` Cortex-R4 initialization and interrupt masking.

---

### 12.7 ARM CoreSight TPIU, SWO, and ITM Stimulus
- `tpiu create tpiu_name configparams...` / `swo ...`: `[Command]` Creates TPIU/SWO object linked to DAP MEM-AP.
  - `-protocol (sync|uart|manchester)`: Synchronous parallel, asynchronous UART NRZ, or Manchester.
  - `-output (external|:port|filename|-)`: Directs trace to external pin, TCP port, file, or Tcl stream.
  - `-traceclk TRACECLKIN_freq`: Frequency of trace clock in Hz (typically HCLK).
  - `-pin-freq trace_freq`: Desired baud rate on SWO pin in Hz.
- `tpiu names` / `tpiu init`: `[Command]` Queries and initializes TPIU instances.
- `$tpiu_name configure` / `cget` / `enable` / `disable`: `[Command]` Configures and activates trace stream capture.
- `itm port port (0|1|on|off)`: `[Command]` Toggles ITM stimulus port `port` (port 0 is default).
- `itm ports (0|1|on|off)`: `[Command]` Enables or disables all 32 ITM stimulus ports.

---

### 12.8 ARMv7-M & Cortex-M Specific Commands
- `cortex_m maskisr (auto|on|off|steponly)`: `[Command]` Manages interrupt servicing during single-step. `auto` services pending interrupts without entering handlers during step. `steponly` suppresses erratum 702596 on Cortex-M7.
- `cortex_m vector_catch [all|none|list]`: `[Command]` Intercepts hardware exceptions: `hard_err`, `mm_err`, `bus_err`, `irq_err`, `state_err`, `chk_err`, `nocp_err`, `reset`.
- `cortex_m reset_config (sysresetreq|vectreset)`: `[Command]` Emulation reset method when hardware SRST is missing:
  - `sysresetreq`: Resets core and all on-chip peripherals via NVIC AIRCR.
  - `vectreset`: Resets core only; leaves peripherals unreset (unsupported on Cortex-M0/M0+/M1).

---

### 12.9 ARMv8-A (AArch64) Architecture
- `aarch64 cache_info`: `[Command]` Displays 64-bit cache levels and geometry.
- `aarch64 dbginit`: `[Command]` Unlocks OS Lock and establishes CTI cross-trigger routing.
- `aarch64 disassemble address [count]`: `[Command]` Disassembles 64-bit A64 instructions.
- `aarch64 smp [on|off]` / `maskisr [on|off]`: `[Command]` SMP run-control and interrupt masking.
- `$target_name catch_exc [off|sec_el1|sec_el3|nsec_el1|nsec_el2]+`: `[Command]` Traps exceptions at Secure and Non-Secure Exception Levels (EL1, EL2, EL3).

---

### 12.10 RISC-V Architecture
- `riscv expose_csrs n[-m|=name] [...]`: `[Config Command]` Exposes standard or custom Control and Status Registers (CSRs) to GDB.
- `riscv expose_custom n[-m|=name] [...]`: `[Config Command]` Exposes custom registers mapped to abstract commands starting at `0xc000`.
- `riscv info`: `[Command]` Displays XLEN (32/64), hart count, debug spec version (0.11 or 0.13), and supported extensions.
- `riscv reset_delays [wait]`: `[Command]` Re-calibrates learned Run-Test/Idle cycles.
- `riscv set_command_timeout_sec [seconds]`: `[Command]` Abstract command timeout.
- `riscv set_reset_timeout_sec [seconds]`: `[Command]` Timeout waiting for harts to exit reset.
- `riscv set_mem_access method1 [method2] [method3]`: `[Command]` Sets memory access priority: `progbuf`, `sysbus`, `abstract`.
- `riscv set_enable_virtual on|off`: `[Command]` Enables virtual memory translation based on satp register.
- `riscv set_enable_virt2phys on|off`: `[Command]` Toggles automatic satp virt2phys address calculation.
- `riscv resume_order normal|reversed`: `[Command]` Configures hart wake order.
- `riscv set_ir (idcode|dtmcs|dmi) [value]`: `[Command]` Overrides JTAG IR values (useful for BSCANE2 primitives).
- `riscv use_bscan_tunnel value`: `[Command]` Enables BSCAN tunneling through FPGA fabric.
- `riscv set_ebreakm on|off` / `set_ebreaks on|off` / `set_ebreaku on|off`: `[Command]` Configures whether `ebreak` in Machine, Supervisor, or User mode traps to OpenOCD or generates internal exceptions.
- `riscv authdata_read` / `authdata_write value`: `[Command]` Authentication challenge-response handshake over debug module.
- `riscv dmi_read address` / `dmi_write address value`: `[Command]` Direct read/write to Debug Module Interface registers.

---

### 12.11 Cadence / Tensilica Xtensa Architecture
- `xtensa xtdef (LX|NX)`: `[Config Command]` Sets Xtensa core architecture generation.
- `xtensa xtopt option value`: `[Config Command]` Configures core parameters: `arnum`, `windowed`, `cpenable`, `exceptions`, `intnum`, `hipriints`, `excmlevel`, `intlevels`, `debuglevel`, `ibreaknum`, `dbreaknum`.
- `xtensa xtmem (iram|dram|sram|irom|drom|srom) baseaddr bytes`: `[Config Command]` Declares on-chip RAM/ROM blocks.
- `xtensa xtmem (icache|dcache) linebytes cachebytes ways [writeback]`: `[Config Command]` Cache geometry.
- `xtensa xtmpu numfgseg minsegsz lockable execonly`: `[Config Command]` Memory Protection Unit configuration.
- `xtensa xtmmu numirefillentries numdrefillentries`: `[Config Command]` MMU TLB configuration.
- `xtensa xtregs numregs`: `[Config Command]` Declares total register count.
- `xtensa xtregfmt (sparse|contiguous) [general]`: `[Config Command]` GDB register map layout.
- `xtensa xtreg name offset`: `[Config Command]` Declares individual core/TIE register.
- `xtensa maskisr (on|off)`: `[Command]` Interrupt masking during instruction stepping.
- `xtensa set_permissive (0|1)`: `[Command]` Skips memory range validation before reads/writes.
- `xtensa smpbreak [none|breakinout|runstall] | [BreakIn] [BreakOut] [RunStallIn] [DebugModeOut]`: `[Command]` Configures inter-core break/stall network.
- `xtensa exe <hex_bytes>`: `[Command]` Injects and executes arbitrary opcode bytes on core.
- `xtensa perfmon_enable <counter_id> <select> [mask] [kernelcnt] [tracelevel]`: `[Command]` Starts hardware performance counters.
- `xtensa perfmon_dump (counter_id)`: `[Command]` Reads performance counter value.
- `xtensa tracestart [pc <pcval>/[<maskbitcount>]] [after <n> [ins|words]]`: `[Command]` Initiates execution trace.
- `xtensa tracestop`: `[Command]` Halts trace.
- `xtensa tracedump <outfile>`: `[Command]` Dumps trace memory to disk.

---

### 12.12 Synopsys ARC Architecture
- `arc add-reg -name name -num number -feature XML_feature [-gdbnum n] [-core] [-bcr] [-type type] [-g]`: `[Config Command]` Defines custom core or auxiliary (AUX) registers.
- `arc add-reg-type-flags -name name flags...`: `[Config Command]` Defines 1-bit flag register layout.
- `arc add-reg-type-struct -name name structs...`: `[Config Command]` Defines structured bitfield register type.
- `arc get-reg-field reg-name field-name`: `[Command]` Extracts bitfield value from struct register.
- `arc set-reg-exists reg-names...`: `[Command]` Dynamically validates existence of optional registers.
- `arc jtag set-aux-reg regnum value` / `get-aux-reg regnum`: `[Command]` Uncached direct JTAG access to AUX registers.
- `arc jtag set-core-reg regnum value` / `get-core-reg regnum`: `[Command]` Direct JTAG access to core registers.

---

### 12.13 EnSilica eSi-RISC Architecture
- `esirisc cache_arch (harvard|von_neumann)`: `[Command]` Cache memory architecture.
- `esirisc hwdc (all|none|mask ...)`: `[Command]` Controls exception interception in HWDC register.
- `esirisc flush_caches`: `[Command]` Flushes instruction and data caches.
- `esirisc trace buffer address size [wrap]` / `trace fifo address`: `[Command]` Configures trace storage.
- `esirisc trace flow_control (enable|disable)`: `[Command]` CPU stalling on trace FIFO overflow.
- `esirisc trace format (full|branch|icache) pc_bits`: `[Command]` Sets trace encoding format.
- `esirisc trace trigger start` / `stop (condition) [data mask]`: `[Command]` Trace triggers.
- `esirisc trace trigger delay (trigger) [cycles]`: `[Command]` Trigger delay in clock cycles.
- `esirisc trace init` / `info` / `status` / `start` / `stop`: `[Command]` Trace lifecycle management.
- `esirisc trace analyze [address size]` / `dump [address size] filename`: `[Command]` Analyzes or dumps trace data.

---

### 12.14 Intel Quark (IA-32 / x86) Architecture
- `x86_32 idw address`: `[Command]` Reads 32-bit port from x86 I/O address space (`0x0000 - 0xffff`).
- `x86_32 idh address`: `[Command]` Reads 16-bit port from x86 I/O space.
- `x86_32 idb address`: `[Command]` Reads 8-bit port from x86 I/O space.
- `x86_32 iww address`: `[Command]` Writes 32-bit value to x86 I/O port.
- `x86_32 iwh address`: `[Command]` Writes 16-bit value to x86 I/O port.
- `x86_32 iwb address`: `[Command]` Writes 8-bit value to x86 I/O port.

---

### 12.15 OpenRISC 1000 Architecture
- `tap_select (vjtag|mohor|xilinx_bscan)`: `[Command]` Selects JTAG TAP interface type.
- `du_select (adv|mohor) [option]`: `[Command]` Selects Advanced Debug Interface (`adv`) or classic Mohor core. Option `1` enables high-speed bursts.
- `addreg [name] [address] [feature] [reg_group]`: `[Command]` Adds custom register to CPU descriptor.

---

### 12.16 Software Tracing & DCC Messages (`libdcc`)
- `target_request debugmsgs [enable|disable|charmsg]`: `[Command]` Intercepts debug messages sent over JTAG DCC channel from target firmware. `charmsg` enables raw character mode for Linux `CONFIG_DEBUG_ICEDCC`.
- `trace history [clear|count]`: `[Command]` Manages circular buffer of 24-bit software trace points emitted by `libdcc`.
- `trace point [clear|identifier]`: `[Command]` Configures software execution trace point counters.

---
## 13. Low-Level JTAG & Boundary Scan Commands

### 13.1 Low-Level JTAG Scan Operations

#### drscan
- **Syntax**: `drscan tap [numbits value]+ [-endstate tap_state]`
- **Mode**: `[Command]`
- **Description**: Shifts fields into the Data Register of `tap` while all other TAPs are held in `BYPASS`. Returns the previous register contents shifted out of TDO. `tap_state` sets end state (defaults to `run/idle`).

#### irscan
- **Syntax**: `irscan [tap instruction]+ [-endstate tap_state]`
- **Mode**: `[Command]`
- **Description**: Loads instruction opcodes into the Instruction Registers of specified TAPs while placing remaining TAPs in `BYPASS`.

#### pathmove
- **Syntax**: `pathmove start_state [next_state ...]`
- **Mode**: `[Command]`
- **Description**: Transitions the JTAG TAP finite state machine through an explicit series of legal state transitions, one TCK cycle per state. States must be stable or legal next-states.

#### runtest
- **Syntax**: `runtest num_cycles`
- **Mode**: `[Command]`
- **Description**: Transitions FSM to `Run-Test/Idle` and pulses TCK for at least `num_cycles`.

#### flush_count
- **Syntax**: `flush_count`
- **Mode**: `[Command]`
- **Description**: Returns the count of JTAG queue flushes across the host USB/Ethernet link (useful for batching performance optimization).

#### verify_ircapture
- **Syntax**: `verify_ircapture (enable|disable)`
- **Mode**: `[Command]`
- **Description**: Validates that ircapture returns the standard `...01` binary pattern during IR scans.

#### verify_jtag
- **Syntax**: `verify_jtag (enable|disable)`
- **Mode**: `[Command]`
- **Description**: Validates both DR and IR scan integrity.

---

### 13.2 Boundary Scan Test (SVF, XSVF, IPDBG)

#### svf
- **Syntax**: `svf filename [-tap tapname] [[-]quiet] [[-]nil] [[-]progress] [[-]ignore_error]`
- **Mode**: `[Command]`
- **Description**: Resets TAP state machine and executes Serial Vector Format test vectors from `filename`.
  - `-tap tapname`: Dynamically calculates IR/DR headers and footers to target a specific TAP on a multi-device scan chain.
  - `-quiet`: Suppresses per-vector logging.
  - `-nil`: Dry-run mode; parses file without driving hardware pins.
  - `-progress`: Outputs execution progress.
  - `-ignore_error`: Continues execution despite TDO comparison errors.

#### xsvf
- **Syntax**: `xsvf (tapname|plain) filename [virt2] [quiet]`
- **Mode**: `[Command]`
- **Description**: Executes binary Xilinx Serial Vector Format files for FPGA/CPLD configuration. `virt2` interprets delay counts as TCK cycles instead of microseconds.

#### ipdbg
- **Syntax**: `ipdbg [-start|-stop] -tap tapname -hub ir_value [dr_length] [-port number] [-tool number] [-vir [vir_value [length [instr_code]]]]`
- **Mode**: `[Command]`
- **Description**: Starts or stops an IPDBG JTAG-Host TCP gateway server for internal logic analyzer and waveform generator IP cores.

---
## 14. RAM Testing & Firmware Recovery Utilities

OpenOCD provides Tcl memory testing scripts in `tools/memtest.tcl`:

### memTestDataBus
- **Syntax**: `memTestDataBus address`
- **Mode**: `[Command]`
- **Description**: Performs a walking 1's test on the target data bus at `address` to detect open pins, shorts to VDD/GND, and solder bridges.

### memTestAddressBus
- **Syntax**: `memTestAddressBus baseaddress size`
- **Mode**: `[Command]`
- **Description**: Performs walking 1's test across address bits to detect address line aliasing and stuck-at faults.

### memTestDevice
- **Syntax**: `memTestDevice baseaddress size`
- **Mode**: `[Command]`
- **Description**: Verifies storage cell integrity by performing increment/decrement patterns across the entire memory range, verifying every bit as `0` and `1`.

### runAllMemTests
- **Syntax**: `runAllMemTests baseaddress size`
- **Mode**: `[Command]`
- **Description**: Executes `memTestDataBus`, `memTestAddressBus`, and `memTestDevice` sequentially across the specified RAM block.

### Firmware Recovery Helpers
- Quickstart script for consumer device unbricking: `openocd -f tools/firmware-recovery.tcl -c firmware_help`.

---
## 15. GDB Configuration & Server Control Commands

### gdb_breakpoint_override
- **Syntax**: `gdb_breakpoint_override [hard|soft|disable]`
- **Mode**: `[Command]`
- **Description**: Forces breakpoint allocation type for incoming GDB break commands. Overcomes limitations of IDEs that fail to differentiate hardware vs. software breakpoints.

### gdb_flash_program
- **Syntax**: `gdb_flash_program (enable|disable)`
- **Mode**: `[Config Command]`
- **Description**: Enables OpenOCD to execute flash programming upon receiving GDB `vFlash` packets during `load` commands (default: `enable`).

### gdb_memory_map
- **Syntax**: `gdb_memory_map (enable|disable)`
- **Mode**: `[Config Command]`
- **Description**: Transmits target memory map XML descriptions to GDB via `qXfer:memory-map:read` packets (default: `enable`).

### gdb_report_data_abort
- **Syntax**: `gdb_report_data_abort (enable|disable)`
- **Mode**: `[Config Command]`
- **Description**: Specifies whether memory access data aborts return error packets to GDB (default: `disable`).

### gdb_report_register_access_error
- **Syntax**: `gdb_report_register_access_error (enable|disable)`
- **Mode**: `[Config Command]`
- **Description**: Returns error packets when GDB attempts reading/writing unsupported registers (default: `disable`).

### gdb_target_description
- **Syntax**: `gdb_target_description (enable|disable)`
- **Mode**: `[Config Command]`
- **Description**: Transmits architectural register descriptions to GDB via `qXfer:features:read` packets (default: `enable`).

### gdb_save_tdesc
- **Syntax**: `gdb_save_tdesc`
- **Mode**: `[Command]`
- **Description**: Dumps target XML register description file (`target_name.xml`) to the local file system.

---
## 16. Jim-Tcl Scripting API & RPC Server Commands

### capture
- **Syntax**: `capture <command>`
- **Mode**: `[Command]`
- **Description**: Executes arbitrary OpenOCD command string `<command>` and intercepts all server log output generated during execution, returning the log text as a single Tcl result string.
- **Example**:
  ```tcl
  set log_data [capture "reset init"]
  echo "Captured log: $log_data"
  ```

### tcl_notifications
- **Syntax**: `tcl_notifications [on/off]`
- **Mode**: `[Command]`
- **Description**: Toggles unprompted asynchronous target notifications over the Tcl RPC socket interface. Emits associative arrays for:
  - `type target_event event <event_name>`
  - `type target_state state <state_name>`
  - `type target_reset mode <reset_mode>`

### tcl_trace
- **Syntax**: `tcl_trace [on/off]`
- **Mode**: `[Command]`
- **Description**: Toggles asynchronous output of hex-encoded target trace data over the Tcl RPC server connection. Emits:
  - `type target_trace data <hex_encoded_trace>`

---
*End of Exhaustive OpenOCD 0.12.0 Command & Driver Reference Manual.*
