
import queue
import re
import subprocess
import threading
import time

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class GDBResult:
    command: str
    result: str
    output: list[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.result != "error" and self.error is None


class GDBManager:
    """
    Persistent GDB manager using the GDB/MI2 interface.

    MI is used for structured communication.
    Console commands provide access to the complete GDB CLI.
    """

    def __init__(self, gdb_path: Path | str):
        self.gdb_path = str(gdb_path)

        self.process = None
        self.reader_thread = None

        self.running = False
        self.token = 0

        self.response_queue = queue.Queue()
        self.event_queue = queue.Queue()

        self.command_lock = threading.Lock()
        self.prompt_event = threading.Event()

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    @staticmethod
    def _quote_mi(value: str) -> str:
        """Escape a string for a GDB/MI quoted argument."""
        value = str(value)
        value = value.replace("\\", "\\\\")
        value = value.replace('"', '\\"')
        value = value.replace("\n", "\\n")
        return f'"{value}"'

    @staticmethod
    def _decode_mi_string(value: str) -> str:
        """Decode a basic MI C-style quoted string."""
        try:
            return bytes(value, "utf-8").decode("unicode_escape")
        except (UnicodeDecodeError, ValueError):
            return value

    def _read_output(self):
        """Continuously read GDB output without blocking commands."""
        while self.process and self.process.stdout:
            line = self.process.stdout.readline()

            if not line:
                break

            line = line.strip()

            if not line:
                continue

            if line == "(gdb)":
                self.prompt_event.set()
                continue

            self.response_queue.put(line)

        self.running = False

    def _next_token(self) -> int:
        self.token += 1
        return self.token

    def _check_process(self):
        if not self.process:
            raise RuntimeError("GDB is not started")

        if self.process.poll() is not None:
            raise RuntimeError(
                f"GDB process has exited with code {self.process.returncode}"
            )

    # ---------------------------------------------------------
    # Start and stop GDB
    # ---------------------------------------------------------

    def start(self, timeout: int = 10) -> int:
        """Start a persistent GDB MI2 process."""

        if self.running:
            return self.process.pid

        self.prompt_event.clear()
        while not self.response_queue.empty():
            try:
                self.response_queue.get_nowait()
            except queue.Empty:
                break
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
            except queue.Empty:
                break

        self.process = subprocess.Popen(
            [
                self.gdb_path,
                "--quiet",
                "--nx",
                "--interpreter=mi2",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        self.running = True

        self.reader_thread = threading.Thread(
            target=self._read_output,
            daemon=True,
        )
        self.reader_thread.start()

        if not self.prompt_event.wait(timeout):
            self.stop()
            raise TimeoutError("GDB did not become ready")

        # Enable asynchronous execution.
        self.execute_mi("-gdb-set mi-async on", timeout=timeout)

        return self.process.pid

    def stop(self):
        """Gracefully stop GDB, then force termination if necessary."""

        if not self.process:
            return

        if self.process.poll() is None:
            try:
                self.execute_mi("-gdb-exit", timeout=3)
            except Exception:
                pass

            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.terminate()

                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()

        for stream in (
            self.process.stdin,
            self.process.stdout,
            self.process.stderr,
        ):
            if stream:
                stream.close()

        self.process = None
        self.running = False
        self.prompt_event.clear()

    def get_status(self) -> dict:
        return {
            "running": self.running,
            "pid": self.process.pid if self.process else None,
        }

    # ---------------------------------------------------------
    # GDB/MI command execution
    # ---------------------------------------------------------

    def execute_mi(
        self,
        command: str,
        timeout: int = 10,
    ) -> GDBResult:
        """
        Execute any supported GDB/MI command.

        Example:
            execute_mi("-thread-info")
            execute_mi("-data-list-register-values x")
        """

        self._check_process()

        with self.command_lock:
            token = self._next_token()
            command_line = f"{token}{command}"

            self.process.stdin.write(command_line + "\n")
            self.process.stdin.flush()

            output = []
            deadline = time.monotonic() + timeout

            while time.monotonic() < deadline:
                self._check_process()

                remaining = deadline - time.monotonic()

                try:
                    line = self.response_queue.get(timeout=remaining)
                except queue.Empty:
                    break

                # MI result record: token^done, token^error, etc.
                match = re.match(r"^(\d+)\^([a-zA-Z_-]+)(?:,(.*))?$", line)

                if match:
                    response_token = int(match.group(1))

                    if response_token != token:
                        self.event_queue.put(line)
                        continue

                    result_type = match.group(2)
                    result_data = match.group(3) or ""

                    error = None

                    if result_type == "error":
                        error_match = re.search(
                            r'msg="((?:\\.|[^"])*)"',
                            result_data,
                        )

                        error = (
                            self._decode_mi_string(error_match.group(1))
                            if error_match
                            else result_data
                        )

                    if result_data and result_data not in output:
                        output.append(result_data)

                    return GDBResult(
                        command=command,
                        result=result_type,
                        output=output,
                        error=error,
                    )

                # Async execution records.
                if line.startswith(("*", "+", "=")):
                    self.event_queue.put(line)
                    continue

                # Stream records.
                if line.startswith(("~", "@", "&")):
                    output.append(line[1:])
                    continue

                output.append(line)

            raise TimeoutError(
                f"GDB command timed out: {command}"
            )

    # ---------------------------------------------------------
    # Generic GDB command execution
    # ---------------------------------------------------------

    def execute_command(
        self,
        command: str,
        timeout: int = 10,
    ) -> GDBResult:
        """
        Execute any GDB CLI command through MI.

        Examples:
            execute_command("info registers")
            execute_command("info breakpoints")
            execute_command("monitor reset halt")
            execute_command("compare-sections")
        """

        if not command or not command.strip():
            raise ValueError("GDB command cannot be empty")

        mi_command = (
            "-interpreter-exec console "
            + self._quote_mi(command)
        )

        return self.execute_mi(mi_command, timeout)

    # ---------------------------------------------------------
    # ELF and target connection
    # ---------------------------------------------------------

    def load_elf(self, elf_path: Path | str) -> GDBResult:
        """Load ELF symbols into GDB."""

        path = Path(elf_path).resolve()

        if not path.is_file():
            raise FileNotFoundError(f"ELF file not found: {path}")

        return self.execute_mi(
            "-file-exec-and-symbols " + self._quote_mi(str(path))
        )

    def connect(
        self,
        host: str = "localhost",
        port: int = 3333,
    ) -> GDBResult:
        """Connect GDB to the OpenOCD GDB server."""

        if not 1 <= port <= 65535:
            raise ValueError("Invalid GDB server port")

        res = self.execute_mi(
            "-target-select extended-remote "
            f"{host}:{port}"
        )
        if not res.success:
            res = self.execute_mi(
                "-target-select remote "
                f"{host}:{port}"
            )
        return res

    def disconnect(self) -> GDBResult:
        return self.execute_mi("-target-disconnect")

    def flash(self) -> GDBResult:
        """Program the connected target using the loaded ELF."""

        return self.execute_command("load", timeout=120)

    def verify_flash(self) -> GDBResult:
        return self.execute_command("compare-sections", timeout=120)

    # ---------------------------------------------------------
    # Target execution control
    # ---------------------------------------------------------

    def halt(self) -> GDBResult:
        return self.execute_mi("-exec-interrupt")

    def continue_execution(self) -> GDBResult:
        return self.execute_mi("-exec-continue")

    def step(self) -> GDBResult:
        return self.execute_mi("-exec-step")

    def next(self) -> GDBResult:
        return self.execute_mi("-exec-next")

    def finish(self) -> GDBResult:
        return self.execute_mi("-exec-finish")

    def reset(self, halt: bool = True) -> GDBResult:
        command = "monitor reset halt" if halt else "monitor reset run"
        return self.execute_command(command)

    def wait_for_stop(self, timeout: int = 30) -> Optional[str]:
        """
        Wait for an asynchronous target stop event.

        Useful after continue_execution().
        """

        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            try:
                event = self.event_queue.get(
                    timeout=max(0.01, deadline - time.monotonic())
                )
            except queue.Empty:
                return None

            if event.startswith("*stopped"):
                return event

        return None

    # ---------------------------------------------------------
    # Breakpoints and watchpoints
    # ---------------------------------------------------------

    def add_breakpoint(self, location: str) -> GDBResult:
        return self.execute_mi(
            "-break-insert " + self._quote_mi(location)
        )

    def remove_breakpoint(self, breakpoint_id: str) -> GDBResult:
        return self.execute_mi(
            f"-break-delete {breakpoint_id}"
        )

    def list_breakpoints(self) -> GDBResult:
        return self.execute_mi("-break-list")

    def add_watchpoint(
        self,
        expression: str,
        access: str = "write",
    ) -> GDBResult:
        options = {
            "write": "-break-watch",
            "read": "-break-watch -r",
            "access": "-break-watch -a",
        }

        if access not in options:
            raise ValueError("access must be write, read, or access")

        return self.execute_mi(
            f"{options[access]} "
            + self._quote_mi(expression)
        )

    # ---------------------------------------------------------
    # Registers, memory and variables
    # ---------------------------------------------------------

    def get_registers(self) -> GDBResult:
        return self.execute_command("info registers")

    def get_register_values(self, format: str = "x") -> GDBResult:
        if format not in ("x", "o", "t", "d", "r"):
            raise ValueError("Unsupported register format")

        return self.execute_mi(
            f"-data-list-register-values {format}"
        )

    def read_memory(
        self,
        address: str,
        count: int = 1,
        word_size: int = 4,
    ) -> GDBResult:
        if count < 1 or word_size not in (1, 2, 4, 8):
            raise ValueError("Invalid memory read parameters")

        # Map word size (bytes) to GDB size suffix: 1->b, 2->h, 4->w, 8->g
        size_map = {1: 'b', 2: 'h', 4: 'w', 8: 'g'}
        suffix = size_map.get(word_size)
        if suffix is None:
            raise ValueError("word_size must be 1, 2, 4 or 8")
        return self.execute_command(
            f"x/{count}{suffix} {address}"
        )

    def write_memory(
        self,
        address: str,
        value: str,
        word_size: int = 4,
    ) -> GDBResult:
        if word_size not in (1, 2, 4, 8):
            raise ValueError("word_size must be 1, 2, 4 or 8")

        return self.execute_command(
            f"set {{unsigned int{word_size * 8}_t}}"
            f"{address} = {value}"
        )

    def evaluate(self, expression: str) -> GDBResult:
        return self.execute_mi(
            "-data-evaluate-expression "
            + self._quote_mi(expression)
        )

    def get_local_variables(self) -> GDBResult:
        return self.execute_mi("-stack-list-locals 1")

    # ---------------------------------------------------------
    # Stack, source and disassembly
    # ---------------------------------------------------------

    def get_backtrace(self) -> GDBResult:
        return self.execute_mi("-stack-list-frames")

    def get_stack_arguments(self) -> GDBResult:
        return self.execute_mi("-stack-list-arguments 1")

    def get_source(self) -> GDBResult:
        return self.execute_command("list")

    def disassemble(self, location: str = "$pc") -> GDBResult:
        return self.execute_command(
            f"disassemble {location}"
        )

    def get_threads(self) -> GDBResult:
        return self.execute_mi("-thread-info")

    # ---------------------------------------------------------
    # Generic information and event access
    # ---------------------------------------------------------

    def get_info(self, topic: str) -> GDBResult:
        return self.execute_command(f"info {topic}")

    def get_target_state(self) -> GDBResult:
        return self.execute_command("info program")

    def get_event(self, timeout: float = 0.1) -> Optional[str]:
        try:
            return self.event_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    # ---------------------------------------------------------
    # Context manager support
    # ---------------------------------------------------------

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
