
import subprocess
import os


class SessionManager:

    def __init__(self):
        self.openocd = None
        self.gdb = None

    # --------------------------------
    # Start OpenOCD
    # --------------------------------

    def start_openocd(self, command):
        """Start OpenOCD in a separate console."""

        if self.is_running(self.openocd):
            raise RuntimeError("OpenOCD is already running")

        creation_flags = (
            subprocess.CREATE_NEW_CONSOLE
            if os.name == "nt"
            else 0
        )

        self.openocd = subprocess.Popen(
            command,
            creationflags=creation_flags
        )

        return self.openocd.pid

    # --------------------------------
    # Start GDB
    # --------------------------------

    def start_gdb(self, command):
        """Start GDB with pipes for MCP communication."""

        if self.is_running(self.gdb):
            raise RuntimeError("GDB is already running")

        self.gdb = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1
        )

        return self.gdb.pid

    # --------------------------------
    # Process status
    # --------------------------------

    @staticmethod
    def is_running(process):
        """Check whether a process is running."""

        return (
            process is not None
            and process.poll() is None
        )

    def get_status(self):
        """Get OpenOCD and GDB status."""

        return {
            "openocd": self.is_running(self.openocd),
            "gdb": self.is_running(self.gdb)
        }

    # --------------------------------
    # Stop individual processes
    # --------------------------------

    @staticmethod
    def stop_process(process, timeout=5):
        """Terminate a process and close its pipes."""

        if process is None:
            return

        if process.poll() is None:
            process.terminate()

            try:
                process.wait(timeout=timeout)

            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        # Close stdin/stdout/stderr if available
        for stream in (
            process.stdin,
            process.stdout,
            process.stderr
        ):
            if stream is not None and not stream.closed:
                stream.close()

    # --------------------------------
    # Stop GDB
    # --------------------------------

    def stop_gdb(self):
        """Stop GDB process."""

        self.stop_process(self.gdb)
        self.gdb = None

    # --------------------------------
    # Stop OpenOCD
    # --------------------------------

    def stop_openocd(self):
        """Stop OpenOCD process."""

        self.stop_process(self.openocd)
        self.openocd = None

    # --------------------------------
    # Close all sessions
    # --------------------------------

    def close(self):
        """Terminate all active processes."""

        self.stop_gdb()
        self.stop_openocd()


session_manager = SessionManager()
