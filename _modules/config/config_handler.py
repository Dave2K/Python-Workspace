"""
File: config_handler.py
Gestione centralizzata della configurazione con validazione integrata.
Include:
- Caricamento da file JSON
- Creazione configurazione di default
- Validazione avanzata
- Gestione dei placeholder
"""

import os
import json
import datetime
import re
from _modules.logging.logging import configure_logging, create_logger

# Crea il logger utilizzando la tua classe di logging
logger = create_logger(__name__)

class Config:
    """
    Classe base per la gestione della configurazione con supporto per placeholders e validazione.
    
    Attributi:
        SUPPORTED_PLACEHOLDERS (list): Lista di placeholder supportati.
        DEFAULT_FILE_NAME_CONFIG (str): Nome del file di configurazione di default.
        config (dict): Dizionario che contiene la configurazione caricata.
        config_file_path (str): Percorso del file di configurazione.
    
    Metodi:
        load(): Carica la configurazione da un file JSON.
        get(key): Ottiene il valore di una chiave di configurazione.
        get_output_file_path(target_path_folder, output_template): Calcola il percorso del file di output sostituendo i placeholder.
        validate(): Metodo per validare la configurazione, da implementare nelle classi concrete.
        to_dict(): Restituisce la configurazione come dizionario.
        from_dict(data): Crea un'istanza da un dizionario.
    """
    
    SUPPORTED_PLACEHOLDERS = ["{target}", "{timestamp}"]
    DEFAULT_FILE_NAME_CONFIG = "config.json"

    def __init__(self, config_file_path=None):
        """
        Inizializza la configurazione.
        Carica la configurazione dal file se esistente, altrimenti crea una configurazione di default.

        :param config_file_path: Percorso del file di configurazione (opzionale)
        """
        self.config_file_path = config_file_path or Config.DEFAULT_FILE_NAME_CONFIG
        self.config = {}
        self.load()

    def load(self):
        """
        Carica la configurazione da un file JSON.
        Se il file non esiste, crea una configurazione di default.

        :raises: json.JSONDecodeError, IOError se il file non è valido o non può essere letto.
        """
        if os.path.exists(self.config_file_path):
            try:
                with open(self.config_file_path, "r") as f:
                    self.config = json.load(f)
                logger.debug(f"Configurazione caricata da {self.config_file_path}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Errore caricamento config: {str(e)}")

    def _write_file(self):
        """
        Scrive la configurazione su un file JSON.

        :raises: IOError se non è possibile scrivere sul file.
        """
        try:
            with open(self.config_file_path, "w") as f:
                json.dump(self.config, f, indent=4)
            logger.debug(f"Configurazione scritta su {self.config_file_path}")
        except IOError as e:
            logger.error(f"Errore durante la scrittura del file di configurazione: {str(e)}")

    def get(self, key):
        """
        Restituisce il valore di una chiave nella configurazione.

        :param key: La chiave da cercare nel dizionario di configurazione.
        :return: Il valore associato alla chiave o None se non esiste.
        """
        return self.config.get(key)

    def get_output_file_path(self, target_path_folder, output_template):
        """
        Calcola il percorso del file di output sostituendo i placeholder nel template.
        
        :param target_path_folder: Percorso della cartella target.
        :param output_template: Template del percorso del file di output con placeholders.
        :return: Il percorso di output generato con i valori sostituiti.
        :raises: ValueError se il template contiene un placeholder non supportato.
        """
        logger.debug(f"Inizio calcolo percorso di output per: {target_path_folder}")

        if not target_path_folder:
            logger.error("Il percorso della cartella target è vuoto")
            raise ValueError("Il percorso della cartella target è vuoto")

        target_name = os.path.basename(os.path.normpath(target_path_folder))
        logger.debug(f"Nome della cartella target: {target_name}")

        if not output_template:
            logger.error("Il template di output è vuoto")
            raise ValueError("Il template di output è vuoto")

        for placeholder in self._extract_placeholders(output_template):
            if placeholder not in self.SUPPORTED_PLACEHOLDERS:
                logger.error(f"Il template contiene un placeholder non supportato: {placeholder}")
                raise ValueError(f"Il template contiene un placeholder non supportato: {placeholder}")

        placeholders = {
            "target": target_name,
            "timestamp": datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        logger.debug(f"Placeholders: {placeholders}")

        try:
            output_file = output_template.format(**placeholders)
            logger.debug(f"Percorso di output generato: {output_file}")
        except KeyError as e:
            logger.error(f"Errore durante la sostituzione dei placeholder: {str(e)}")
            raise KeyError(f"Placeholder non valido nel template: {str(e)}")

        return output_file

    def _extract_placeholders(self, template):
        """
        Estrae i placeholder da una stringa di template.

        :param template: Stringa contenente i placeholder (es. "{target}.xml").
        :return: Lista dei placeholder trovati.
        """
        return re.findall(r"\{[^}]+\}", template)

    def validate(self):
        """
        Valida la configurazione. Metodo da implementare nelle classi concrete.

        :return: Tupla (successo: bool, messaggio: str).
        """
        raise NotImplementedError("Il metodo 'validate' deve essere implementato nella classe concreta")

    def to_dict(self):
        """
        Restituisce la configurazione come un dizionario.

        :return: Il dizionario della configurazione.
        """
        return self.config

    @classmethod
    def from_dict(cls, data):
        """
        Crea un'istanza della configurazione a partire da un dizionario.

        :param data: Il dizionario con i dati di configurazione.
        :return: Una tupla contenente l'istanza della configurazione, un booleano che indica se la creazione è riuscita, e un messaggio di stato.
        """
        config = cls()
        config.config = data
        return config, True, "Configurazione creata correttamente"
