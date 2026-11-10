import ctypes, subprocess, sys, os

def run_as_admin(args: list[str]) -> subprocess.CompletedProcess:
    """Run the given command list with administrator rights on Windows.
    If the current process already has admin privileges the command is executed directly.
    Otherwise the function re‑launches the current interpreter with elevation and then exits.
    """
    # Check if we already have admin rights
    if ctypes.windll.shell32.IsUserAnAdmin():
        return subprocess.run(args, capture_output=True, text=True, check=False)
    # Not admin – re‑invoke with elevation (this will pop up the UAC prompt)
    cmd = [sys.executable] + args
    params = " ".join(f'"{a}"' for a in cmd)
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)

