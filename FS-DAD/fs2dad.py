"""
Main script per la generazione di XML da filesystem.
Include:
- Gestione parametri CLI
- Integrazione con configurazione
- Logging avanzato
"""

# Import necessari per il path e logging
import sys
from pathlib import Path
# Aggiungi la root del progetto al PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from _modules.logging.logging import configure_logging, create_logger
# Configurazione iniziale del sistema di logging
# configure_logging(
#     max_log_files=5,
#     file_level=logging.DEBUG,
#     console_level=logging.INFO,
#     file_format="%(asctime)s | %(levelname)s | %(message)s",
#     console_format="%(levelname)s | %(message)s"
# )
# Configurazione avanzata con tutte le opzioni
import logging
configure_logging(
    # Cartelle e livelli base
    log_folder="_logs",
    log_level=logging.DEBUG,
    
    # Configurazione Console
    enable_console_logging=True,
    console_level=logging.INFO,
    console_format="%(asctime)s - %(levelname)-8s - %(module)-12s - %(message)s",
    
    # Configurazione File
    enable_file_logging=True,
    file_level=logging.DEBUG,
    file_format="%(asctime)s | %(levelname)-8s | %(threadName)-10s | %(module)-15s | %(message)s",
    
    # Naming file
    file_prefix="",
    log_name_source=True,
    script_name_override=Path(__file__).stem,  # Prende il nome di questo file
    enable_timestamp=False,
    file_extension="log",
    
    # Rotazione log
    max_log_files=5
)

# Crea il logger per il modulo corrente
logger = create_logger(__name__)

# Import successivi
import os
import argparse
from app_config import AppConfig 
from xml_generator import create_xml_with_indent
    
def load_or_create_config(config_file):
    """
    Carica o crea la configurazione.
    :param config_file: Percorso del file di configurazione
    :return: Tupla (config: AppConfig, messaggio: str)
    """
    try:
        # Se il file non esiste, crea la configurazione di default
        if not os.path.exists(config_file):
            default_config = AppConfig()
            default_config.write()  # Crea il file di configurazione di default
            return None, f"File non trovato: {config_file}. File config di default creato: {config_file}"

        app_config = AppConfig(config_file_path=config_file)
        # Carica la configurazione dal file
        success, msg = app_config.load()
        
        # Se il caricamento è riuscito, ritorna la configurazione, altrimenti ritorna il messaggio di errore
        if success:
            return app_config, msg
        else:
            return None, msg

    except Exception as e:
        return None, f"Errore critico: {str(e)}"

def main():
    """Punto di ingresso principale."""
    parser = argparse.ArgumentParser(description="Genera XML da struttura cartelle")
    parser.add_argument("--config", help="Percorso file configurazione")
    parser.add_argument("--target", help="Cartella target")
    parser.add_argument("--output", help="File output XML")
    parser.add_argument("--include", help="Pattern inclusione cartelle (separati da virgola)")
    parser.add_argument("--indent-content", help="Parametro opzionale per indentare il contenuto")
    parser.add_argument("--include-files", help="Pattern inclusione file (separati da virgola)")  # <-- UNICA MODIFICA 1/3
    
    args = parser.parse_args()

    # Caricamento configurazione
    config_file = os.path.normpath(args.config)
    app_config, msg = load_or_create_config(config_file)
    if not app_config:
        logger.error(f"Errore configurazione: {msg}")
        return

    # Gestione parametri
    target_path = os.path.normpath(args.target or app_config.target_path_folder)
    if os.path.isfile(target_path):
        logger.error(f"{target_path} è un file, deve essere una cartella")
        return
    elif not os.path.exists(target_path):
        logger.error(f"Cartella non trovata: {target_path}")
        return
    app_config.target_path_folder = target_path            

    output_file = args.output or app_config.config_instance.get_output_file_path(
        app_config.target_path_folder, 
        app_config.output_path_file)
    
    include_folders = args.include.split(",") if args.include else app_config.include_folders
    include_files = args.include_files.split(",") if args.include_files else app_config.include_files  # <-- UNICA MODIFICA 2/3
    
    indent_content = args.indent_content if args.indent_content else app_config.indent_content

    # Generazione XML
    success, message = create_xml_with_indent(
        target_path_folder=app_config.target_path_folder,
        output_file=output_file,
        ignore_folders=app_config.exclude_folders,
        ignore_files=app_config.exclude_files,
        indent= "  " if app_config.indent_content else "",
        include_folders=include_folders,
        indent_content=indent_content,
        include_files=include_files  # <-- UNICA MODIFICA 3/3
    )
    if(success):
        logger.info(message)
    else:
        logger.error(message)

if __name__ == "__main__":
    main()