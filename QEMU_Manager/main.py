# main.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import gi
import logging
from gi.repository import Gtk
from gui import SpiceLauncher
from vm_manager import write_lock, is_running, bring_to_front
from _modules.logging.logging import configure_logging, create_logger

gi.require_version("Gtk", "3.0")

# Configurazione logging
configure_logging(
    enable_file_logging=False,       # Abilita log su file (default: False; alternativamente True)
    file_mode='w',                 # Modalità di apertura file: 'a' per append, 'w' per scrivere (default: 'w')
    log_folder="_logs",            # Cartella in cui salvare i log (default: "logs")
    log_level=logging.INFO,         # Livello globale di log (default: logging.DEBUG)
    enable_console_logging=True,     # Abilita log su console (default: True)
    console_level=logging.DEBUG,  # Livello di log per la console (default: logging.DEBUG)
    console_format={               # Dizionario dei formati per la console per ciascun livello
        'default': "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
        'info': "%(asctime)s - %(name)s - %(message)s",
        'debug': "%(asctime)s - %(levelname)-8s - %(message)s",
    },
    
    console_style="icon"            # Stile per la console: "text", "icon", "both" (default: "text" o "both")
    # Altre opzioni per il file logging sono disponibili, vedi la documentazione
)
logger = create_logger(__name__)

# sopprime il log, lo porta a CRITICAL
logging.getLogger('charset_normalizer').setLevel(logging.CRITICAL)


def launch_gui():
    write_lock()
    app = SpiceLauncher()
    app.connect("destroy", Gtk.main_quit)
    Gtk.main()

if is_running():
    bring_to_front()
else:
    launch_gui()

