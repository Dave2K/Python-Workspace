"""
File: app_config.py
Configurazione concreta per l'applicazione.
Estende la classe base Config e implementa il metodo di validazione.
"""
import os
from _modules.logging.logging import create_logger
# Crea il logger per la classe AppConfig
logger = create_logger(__name__)

from _modules.config.config_handler import Config
from pathlib import Path

class AppConfig():
    """
    Classe concreta per la gestione della configurazione dell'applicazione.
    """

    # Costanti per le chiavi di configurazione
    TARGET_PATH_FOLDER = "target_path_folder"
    OUTPUT_PATH_FILE = "output_path_file"
    INCLUDE_FOLDERS = "include_folders"
    EXCLUDE_FOLDERS = "exclude_folders"
    EXCLUDE_FILES = "exclude_files"
    SPLIT_CONTENT = "split_content"

    DEFAULT_CONFIG = {
        TARGET_PATH_FOLDER: "/Path/Target_Folder",
        OUTPUT_PATH_FILE: "{target}.xml",
        SPLIT_CONTENT: False,
        INCLUDE_FOLDERS: ["*"],
        EXCLUDE_FOLDERS: [
            "bin", "obj", "debug", "release",
            ".vscode", ".vs", "*.git*", 
            "__pycache__", 
            "_artifacts", "_backup", "_temp"
        ],
        EXCLUDE_FILES: [
            ".gitignore", ".gitattributes",
            "*.tmp", "*.log", "*.xml"
        ]
    }

    DEFAULT_FILE_NAME_CONFIG = "config.json"
    MSG_INTERNAL_ERROR = "Errore Interno"

    def __init__(self, config_file_path=None):
        """
        Inizializza la configurazione dell'applicazione.
        Carica la configurazione dal file se esistente, altrimenti crea una configurazione di default.

        :param config_file_path: Percorso del file di configurazione (opzionale)
        """
        self.config_instance = Config()
        self.config_file_path = config_file_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), self.DEFAULT_FILE_NAME_CONFIG)

        # Inizializza i parametri di configurazione con i valori di default
        self.target_path_folder = self.DEFAULT_CONFIG[self.TARGET_PATH_FOLDER]
        self.output_path_file = self.DEFAULT_CONFIG[self.OUTPUT_PATH_FILE]
        self.include_folders = self.DEFAULT_CONFIG[self.INCLUDE_FOLDERS]
        self.exclude_folders = self.DEFAULT_CONFIG[self.EXCLUDE_FOLDERS]
        self.exclude_files = self.DEFAULT_CONFIG[self.EXCLUDE_FILES]
        self.split_content = self.DEFAULT_CONFIG[self.SPLIT_CONTENT]

        # Log per segnalare l'inizializzazione
        logger.debug("Configurazione inizializzata con i valori di default.")

    def from_dict(self, config_data):
        """
        Carica i dati della configurazione da un dizionario.

        :param config_data: Dati di configurazione sotto forma di dizionario
        :return: Tupla (config: AppConfig, messaggio: str)
        """
        # Memorizziamo il percorso del file di configurazione
        # self.config_file_path = config_data.get(self.DEFAULT_FILE_NAME_CONFIG, self.DEFAULT_CONFIG[self.DEFAULT_FILE_NAME_CONFIG])
        self.target_path_folder = config_data.get(self.TARGET_PATH_FOLDER, self.DEFAULT_CONFIG[self.TARGET_PATH_FOLDER])
        self.output_path_file = config_data.get(self.OUTPUT_PATH_FILE, self.DEFAULT_CONFIG[self.OUTPUT_PATH_FILE])
        self.include_folders = config_data.get(self.INCLUDE_FOLDERS, self.DEFAULT_CONFIG[self.INCLUDE_FOLDERS])
        self.exclude_folders = config_data.get(self.EXCLUDE_FOLDERS, self.DEFAULT_CONFIG[self.EXCLUDE_FOLDERS])
        self.exclude_files = config_data.get(self.EXCLUDE_FILES, self.DEFAULT_CONFIG[self.EXCLUDE_FILES])
        self.split_content = config_data.get(self.SPLIT_CONTENT, self.DEFAULT_CONFIG[self.SPLIT_CONTENT])

    def to_dict(self):
        """
        Converte i dati di configurazione dell'istanza in un dizionario.

        :return: Un dizionario con i dati di configurazione
        """
        return {
            # self.DEFAULT_FILE_NAME_CONFIG: self.config_file_path,
            self.TARGET_PATH_FOLDER: self.target_path_folder,
            self.OUTPUT_PATH_FILE: self.output_path_file,
            self.INCLUDE_FOLDERS: self.include_folders,
            self.EXCLUDE_FOLDERS: self.exclude_folders,
            self.EXCLUDE_FILES: self.exclude_files,
            self.SPLIT_CONTENT: self.split_content
        }

    def validate(self):
        """
        Validazione della configurazione dell'applicazione.

        Verifica che i campi obbligatori siano presenti nella configurazione.

        :return: Tupla (successo: bool, messaggio: str)
        """
        required = [self.TARGET_PATH_FOLDER, self.OUTPUT_PATH_FILE]
        for field in required:
            if not getattr(self, field, None):
                return False, f"Campo mancante: {field}"
        return True, "Configurazione valida"
    
    def load(self):
        # success, msg = self.config_instance.load(self)
        # return success, msg
        return self.config_instance.load(self)
    
    def write(self, config_file_path=None):
        config_file_path = config_file_path or self.config_file_path
        self.config_instance.write(self)
        