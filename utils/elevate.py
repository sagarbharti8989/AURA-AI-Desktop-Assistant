import ctypes
import subprocess


def run_as_admin(args: list[str]) -> subprocess.CompletedProcess:
    """Run the given command list with administrator rights on Windows.

    If the current process already has admin privileges the command is executed directly.
    If it does not, the caller receives a clear permission error instead of exiting the
    process unexpectedly.
    """
    if ctypes.windll.shell32.IsUserAnAdmin():
        return subprocess.run(args, capture_output=True, text=True, check=False)

    raise PermissionError(
        "Administrator privileges are required to change Wi‑Fi or Bluetooth settings. "
        "Please run AURA as an administrator or use an elevated session."
    )

