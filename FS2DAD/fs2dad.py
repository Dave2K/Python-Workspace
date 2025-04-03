"""
Main script per la generazione di XML da filesystem.
Integra configurazione, validazione e sistema di help.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from _modules.logging.logging import configure_logging, create_logger
from app_config import AppConfig
from fs_to_dad import fs_to_dad
from help import show_full_help

# Configurazione logging
configure_logging(
    enable_file_logging=True,       # Abilita log su file (default: False; alternativamente True)
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


def apply_cli_overrides(app_config, args):
    """Applica i parametri CLI alla configurazione"""
    if args.target:
        app_config.target_path_folder = os.path.normpath(args.target)
    if args.output:
        app_config.output_path_file = args.output
    if args.include:
        app_config.include_folders = args.include.split(",")
    if args.include_files:
        app_config.include_files = args.include_files.split(",")
    if args.indent_content:
        app_config.indent_content = True

def main():
    parser = argparse.ArgumentParser(
        description="Genera XML da struttura cartelle",
        add_help=False
    )
    
    parser.add_argument("--config", help="Percorso file configurazione")
    parser.add_argument("--target", help="Cartella target")
    parser.add_argument("--output", help="File output XML")
    parser.add_argument("--include", help="Pattern inclusione cartelle")
    parser.add_argument("--indent-content", action='store_true')
    parser.add_argument("--include-files", help="Pattern inclusione file")
    parser.add_argument("--sanitize", help="valida xml")
    parser.add_argument("--help", action='store_true')

    args = parser.parse_args()

    if args.help:
        show_full_help()
        return

    # Gestione config iniziale
    default_config = AppConfig.DEFAULT_FILE_NAME_CONFIG
    config_path = args.config or default_config

    if not any(vars(args).values()) and not os.path.exists(default_config):
        AppConfig().write()
        print(f"\n⚠️ Config creato: {os.path.abspath(default_config)}")
        show_full_help()
        return

    # Caricamento config
    app_config = AppConfig(config_path)
    success, msg = app_config.load() 
    if not success:
        logger.error(f"Caricamento fallito: {msg}")
        return

    # Applica override CLI
    apply_cli_overrides(app_config, args)

    # sostituisce i placeholder 
    app_config.resolve_output_path()
    
    # Generazione XML
    success, message = fs_to_dad(
        target_path_folder=app_config.target_path_folder,
        output_file=app_config.output_path_file,
        indent_chars="  " if app_config.indent_content else "",
        sanitize=app_config.sanitize,
        ignore_folders=app_config.exclude_folders,
        ignore_files=app_config.exclude_files,
        include_folders=app_config.include_folders,
        include_files=app_config.include_files
    )

    # print(f"✅ {message}" if success else f"❌ {message}")
    logger.success(f"{message}")

if __name__ == "__main__":
    main()