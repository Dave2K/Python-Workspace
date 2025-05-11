"""Modulo per gestire il salvataggio e il caricamento delle impostazioni."""
import os
import json

# Percorso del file di configurazione
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "settings.json")
# Configurazione di default
DEFAULT_CONFIG = {
    "last_dir": "/home/davide/Documents/src/Python-Workspace/"
}

def load_config():
    """
    Carica il file settings.json. Se non esiste, lo crea con i valori di DEFAULT_CONFIG.
    Restituisce un dict con le impostazioni.
    """
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    """
    Salva il dict `config` su settings.json (sovrascrivendo).
    """
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
