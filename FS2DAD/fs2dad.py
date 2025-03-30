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
    log_folder="_logs",
    log_level=logging.DEBUG,
    enable_console_logging=True,
    console_level=logging.INFO,
    file_prefix="",
    max_log_files=5
)

logger = create_logger(__name__)

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
    parser.add_argument("--help", action='store_true')

    args = parser.parse_args()

    if args.help:
        show_full_help()
        return

    # Gestione config iniziale
    default_config = "config.json"
    config_path = args.config or default_config

    if not any(vars(args).values()) and not os.path.exists(default_config):
        AppConfig().write()
        print(f"\n⚠️ Config creato: {os.path.abspath(default_config)}")
        show_full_help()
        return

    # try:
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
    
    # Validazione DOPO gli override
    app_config.validate()
    logger.info("✅ Configurazione valida")

    # Generazione XML
    success, message = fs_to_dad(
        target_path_folder=app_config.target_path_folder,
        output_file=app_config.output_path_file,
        ignore_folders=app_config.exclude_folders,
        ignore_files=app_config.exclude_files,
        indent="  " if app_config.indent_content else "",
        include_folders=app_config.include_folders,
        include_files=app_config.include_files
    )

    logger.info(f"🎉 {message}" if success else f"❌ {message}")

    # except ValueError as e:
    #     logger.error(f"❌ Errore validazione:\n{str(e)}")
    # except Exception as e:
    #     logger.error(f"🔥 Errore critico: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()