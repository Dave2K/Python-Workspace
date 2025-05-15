"""Entry point: avvia la GUI."""
import gi
from gui import run_app

gi.require_version("Gtk", "3.0")

if __name__ == "__main__":
    run_app()
