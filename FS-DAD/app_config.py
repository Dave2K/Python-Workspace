"""
File: app_config.py
Configurazione concreta per l'applicazione.
Estende la classe base Config e implementa il metodo di validazione.
"""

from _modules.config.config_handler import Config

class AppConfig(Config):
    """
    Classe concreta per la gestione della configurazione dell'applicazione.
    Estende la classe base Config e implementa il metodo di validazione.
    
    Attributi:
        DEFAULT_CONFIG (dict): La configurazione di default dell'applicazione.
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

    def __init__(self, config_file_path=None):
        """
        Inizializza la configurazione dell'applicazione.
        Carica la configurazione dal file se esistente, altrimenti crea una configurazione di default.

        :param config_file_path: Percorso del file di configurazione (opzionale)
        """
        super().__init__(config_file_path)

    def validate(self):
        """
        Validazione della configurazione dell'applicazione.

        Verifica che i campi obbligatori siano presenti nella configurazione.

        :return: Tupla (successo: bool, messaggio: str)
        """
        required = [self.TARGET_PATH_FOLDER, self.OUTPUT_PATH_FILE]
        for field in required:
            if not self.config.get(field):
                return False, f"Campo mancante: {field}"
        return True, "Configurazione valida"
