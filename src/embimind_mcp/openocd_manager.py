
import json
import socket
import threading
import time
from pathlib import Path

from . import config
from . import target_database
from .session_manager import session_manager


class OpenOCDManager:

    def __init__(self):
        self.rpc_host = "127.0.0.1"
        self.rpc_port = 6666
        self.rpc_socket = None
        self.rpc_lock = threading.Lock()

        self.catalogue_path = (
            Path(__file__).parent
            / "command_catalog"
            / "openocd_commands.json"
        )

    # Start OpenOCD

    def start_openocd(self, board_name: str) -> dict:
        """Start OpenOCD using the registered board configuration."""

        if session_manager.is_running(session_manager.openocd):
            raise RuntimeError("OpenOCD is already running")

        target = target_database.verify_target(board_name)

        command = [
            str(config.OPENOCD_EXE),
            "-s", str(config.OPENOCD_SCRIPTS),
            "-f", target["interface_path"],
            "-c", f"transport select {target['transport']}",
            "-f", target["target_path"],
            "-c", f"tcl_port {self.rpc_port}"
        ]

        pid = session_manager.start_openocd(command)

        try:
            self._connect_rpc()
        except Exception:
            session_manager.stop_openocd()
            raise

        return {
            "status": "started",
            "board": board_name,
            "pid": pid,
            "command": command
        }

    # OpenOCD Status

    def get_openocd_status(self) -> dict:
        """Check OpenOCD process status."""

        return {
            "running": session_manager.is_running(
                session_manager.openocd
            ),
            "rpc_connected": self.rpc_socket is not None
        }

    # Stop OpenOCD

    def stop_openocd(self) -> None:
        """Stop the OpenOCD process."""

        if session_manager.openocd is None:
            raise RuntimeError("OpenOCD has not been started")

        if self.rpc_socket:
            self.rpc_socket.close()
            self.rpc_socket = None

        session_manager.stop_openocd()

    # Connect to OpenOCD Tcl RPC

    def _connect_rpc(self, timeout: int = 10):
        """Establish connection with OpenOCD Tcl RPC server."""

        start_time = time.time()

        while time.time() - start_time < timeout:

            if not session_manager.is_running(session_manager.openocd):
                raise RuntimeError("OpenOCD process terminated")

            try:
                self.rpc_socket = socket.create_connection(
                    (self.rpc_host, self.rpc_port),
                    timeout=1
                )
                self.rpc_socket.settimeout(10)
                return

            except OSError:
                time.sleep(0.2)

        raise TimeoutError("Unable to connect to OpenOCD Tcl RPC")

    # Execute OpenOCD Command

    def execute_command(self, command: str) -> dict:
        """Send a Tcl command to OpenOCD and return its response."""

        if not session_manager.is_running(session_manager.openocd):
            raise RuntimeError("OpenOCD is not running")

        if not command or not command.strip():
            raise ValueError("Command cannot be empty")

        if self.rpc_socket is None:
            self._connect_rpc()

        with self.rpc_lock:

            self.rpc_socket.sendall(
                command.encode("utf-8") + b"\x1a"
            )

            response = bytearray()

            while b"\x1a" not in response:

                data = self.rpc_socket.recv(4096)

                if not data:
                    self.rpc_socket.close()
                    self.rpc_socket = None
                    raise ConnectionError("OpenOCD RPC connection closed")

                response.extend(data)

            result = response.partition(b"\x1a")[0]

            return {
                "command": command,
                "response": result.decode(
                    "utf-8",
                    errors="replace"
                ).strip()
            }

    # Search OpenOCD Command Catalogue

    def search_commands(self, query: str) -> list:
        """Search commands in the OpenOCD JSON catalogue."""

        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        with self.catalogue_path.open("r", encoding="utf-8") as file:
            catalogue = json.load(file)

        query = query.lower().strip()

        results = []

        for entry in catalogue["entries"]:

            searchable_text = " ".join([
                entry.get("name", ""),
                entry.get("syntax", ""),
                entry.get("description", ""),
                entry.get("category", ""),
                entry.get("subcategory", "")
            ]).lower()

            if query in searchable_text:
                results.append(entry)

        return results


# Shared manager instance
openocd_manager = OpenOCDManager()
