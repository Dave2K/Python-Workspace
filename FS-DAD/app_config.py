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
    INDENT_CONTENT = "indent_content"
    INCLUDE_FILES = "include_files"

    # Campi obbligatori
    REQUIRED_FIELDS = [TARGET_PATH_FOLDER, OUTPUT_PATH_FILE]
    # Campi che devono essere percorsi validi
    PATH_FIELDS = [TARGET_PATH_FOLDER, OUTPUT_PATH_FILE]
    # Campi che devono essere liste
    LIST_FIELDS = [INCLUDE_FOLDERS, EXCLUDE_FOLDERS, EXCLUDE_FILES]

    DEFAULT_CONFIG = {
        TARGET_PATH_FOLDER: "/Path/Target_Folder",
        OUTPUT_PATH_FILE: "{target}.xml",
        INDENT_CONTENT: False,
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
        ],
        INCLUDE_FILES: []
    }

    DEFAULT_FILE_NAME_CONFIG = "config.json"

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
        self.indent_content = self.DEFAULT_CONFIG[self.INDENT_CONTENT]
        self.include_files = self.DEFAULT_CONFIG[self.INCLUDE_FILES]

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
        self.indent_content = config_data.get(self.INDENT_CONTENT, self.DEFAULT_CONFIG[self.INDENT_CONTENT])
        self.include_files = config_data.get(self.INCLUDE_FILES, self.DEFAULT_CONFIG[self.INCLUDE_FILES])

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
            self.INDENT_CONTENT: self.indent_content,
            self.INCLUDE_FILES: self.include_files
        }

    # def validate(self):
    #     """
    #     Validazione della configurazione dell'applicazione.

    #     Verifica che i campi obbligatori siano presenti nella configurazione.

    #     :return: Tupla (successo: bool, messaggio: str)
    #     """
    #     required = [self.TARGET_PATH_FOLDER, self.OUTPUT_PATH_FILE]
    #     for field in required:
    #         if not getattr(self, field, None):
    #             return False, f"Campo mancante: {field}"
    #     return True, "Configurazione valida"
    def validate(self):
        """
        Valida i parametri di configurazione.
        Solleva un ValueError se si riscontrano problemi.
        """
        errors = []

        # Controllo campi obbligatori
        for field in self.REQUIRED_FIELDS:
            if not getattr(self, field, None):
                errors.append(f"Il campo {field} è obbligatorio e non può essere vuoto.")

        # Controllo che i percorsi siano validi
        for field in self.PATH_FIELDS:
            path_value = getattr(self, field, None)
            if path_value and not os.path.exists(path_value):
                errors.append(f"Il percorso specificato per {field} non esiste: {path_value}")

        # Controllo che le liste contengano valori validi
        for field in self.LIST_FIELDS:
            list_value = getattr(self, field, None)
            if list_value is not None and not isinstance(list_value, list):
                errors.append(f"Il campo {field} deve essere una lista, ma è di tipo {type(list_value).__name__}.")
            elif list_value:
                for path in list_value:
                    if not isinstance(path, str):
                        errors.append(f"Il campo {field} deve contenere solo stringhe.")

        # Controllo che split_content sia un booleano
        if not isinstance(self.split_content, bool):
            errors.append(f"Il campo {self.SPLIT_CONTENT} deve essere un booleano, ma è {type(self.split_content).__name__}.")

        if errors:
            raise ValueError("\n".join(errors))

    
    def load(self):
        # success, msg = self.config_instance.load(self)
        # return success, msg
        return self.config_instance.load(self)
    
    def write(self, config_file_path=None):
        config_file_path = config_file_path or self.config_file_path
        self.config_instance.write(self)
        