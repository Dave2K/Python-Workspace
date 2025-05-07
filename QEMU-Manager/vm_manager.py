# vm_manager.py

import os
import subprocess
from _modules.logging.logging import create_logger 
logger = create_logger(__name__) 

LOCKFILE = "/tmp/vvm.lock"

def is_running():
    if not os.path.exists(LOCKFILE):
        return False
    try:
        with open(LOCKFILE, "r") as f:
            pid = int(f.read())
        os.kill(pid, 0)
        return True
    except:
        os.remove(LOCKFILE)
        return False

def write_lock():
    with open(LOCKFILE, "w") as f:
        f.write(str(os.getpid()))

def bring_to_front():
    try:
        subprocess.run(["wmctrl", "-a", "SPICE VM Launcher"], check=True)
    except Exception as e:
        logger.error(f"Impossibile portare in primo piano: {e}")
