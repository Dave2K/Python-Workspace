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
from _modules.logging.logging import create_logger

# Crea il logger utilizzando la tua classe di logging
logger = create_logger(__name__)

class Config:
    """
    Classe base per la gestione della configurazione con supporto per placeholders e validazione.
    
    Attributi:
        SUPPORTED_PLACEHOLDERS (list): Lista di placeholder supportati.
    
    Metodi:
        load(): Carica la configurazione da un file JSON.
        get(key): Ottiene il valore di una chiave di configurazione.
        get_output_file_path(template, target_path_folder): Calcola il percorso del file di output sostituendo i placeholder.
    """
    
    SUPPORTED_PLACEHOLDERS = [ "{target}", "{timestamp}", "{sanitize}" ]
    ATTR_REQUIRED = [
        "to_dict",
        "from_dict",
        "config_file_path",
        "REQUIRED_FIELDS"
    ]

    # def __init__(self):
    #     self.config = {}

    def check_hasattr(self, object, method):
        success = False
        msg_err = None
        try:
            if hasattr(object, method):
                success = True
            else:
                msg_err = f"Il metodo {method} nell'oggetto {object} non esiste!"
        except NameError:
            msg_err = f"L'oggetto {object} non esiste!"
        
        return success, msg_err

    def check_attrs(self, app_config_instance):
        # controllo esistenza metodi sulla AppConfig
        success = True
        msg_error = None
        errors = []
        for field in self.ATTR_REQUIRED:
            _success, msg = self.check_hasattr(app_config_instance, field)
            if not _success:
                success = False
                errors.append(msg)
        if not success:
            msg_error = f"Errore in controllo campi in AppConfig: {'\n'.join(errors)}"
            logger.error(msg_error)
        
        return success, msg_error
        

    def load(self, app_config_instance):
        """
        Carica la configurazione da un file JSON.
        Se il file non esiste, crea una configurazione di default.

        :param config_file_path: Percorso del file di configurazione.
        :return: Tupla (success: bool, msg: str)
        """
        # controllo esistenza metodi sulla AppConfig
        success, errors = self.check_attrs(app_config_instance)
        if not success:
            return success, errors

        if os.path.exists(app_config_instance.config_file_path):
            try:
                with open(app_config_instance.config_file_path, "r") as f:
                    config_data = json.load(f)

                # controllo esistenza campi obbligatori nel file config
                success = True
                errors = []
                required = app_config_instance.REQUIRED_FIELDS
                for field in required:  
                    if field not in config_data:
                        errors.append(f"{field} ")
                        success = False  
                if not success:
                    msg_error = f"File config {app_config_instance.config_file_path}\nCampi obbligatori mancanti: {', '.join(errors)}."  
                    logger.error(msg_error)
                    return success, msg_error
        
                # Usa l'istanza di AppConfig per caricare la configurazione
                app_config_instance.from_dict(config_data)
                success = True
                msg = f"File di configurazione caricato: {app_config_instance.config_file_path}."
                logger.debug(msg)
            except (json.JSONDecodeError, IOError) as e:
                msg = f"Errore durante il caricamento del file di configurazione: {str(e)}"
                logger.error(msg)
        else:
            msg = f"File di configurazione non trovato: {app_config_instance.config_file_path}."
            logger.error(msg)
        
        return success, msg

    def write(self, app_config_instance):
        """
        Scrive la configurazione su un file JSON.

        :param config_file_path: Percorso del file di configurazione.
        :return: Tupla (success: bool, msg: str)
        """

        # Controllo se esistono proprietà e metodi necessari su AppConfig
        success, errors = self.check_attrs(app_config_instance)
        if not success:
            return success, errors
        
        try:
            with open(app_config_instance.config_file_path, "w") as f:
                json.dump(app_config_instance.to_dict(), f, indent=4)
            logger.debug(f"Configurazione scritta su {app_config_instance}")
            success = True
            msg = "Configurazione scritta con successo."
        except IOError as e:
            msg = f"Errore durante la scrittura del file di configurazione: {str(e)}"
            logger.error(msg)

        return success, msg

    def get_output_file_path(self, template, target_path_folder):
        """
        Calcola il percorso del file di output sostituendo i placeholder nel template.
        
        :param target_path_folder: Percorso della cartella target.
        :param template: Template del percorso del file di output con placeholders.
        :return: Il percorso di output generato con i valori sostituiti.
        :raises: ValueError se il template contiene un placeholder non supportato.
        """
        logger.debug(f"Inizio calcolo percorso di output per: {target_path_folder}")

        if not target_path_folder:
            logger.error("Il percorso della cartella target è vuoto")
            raise ValueError("Il percorso della cartella target è vuoto")

        target_name = os.path.basename(os.path.normpath(target_path_folder))
        logger.debug(f"Nome della cartella target: {target_name}")

        if not template:
            logger.error("Il template di output è vuoto")
            raise ValueError("Il template di output è vuoto")

        for placeholder in self._extract_placeholders(template):
            if placeholder not in self.SUPPORTED_PLACEHOLDERS:
                logger.error(f"Il template contiene un placeholder non supportato: {placeholder}")
                raise ValueError(f"Il template contiene un placeholder non supportato: {placeholder}")

        placeholders = {
            "target": target_name,
            "timestamp": datetime.datetime.now().strftime("_%Y%m%d_%H%M%S"),
            "sanitize": "_sanitized"
        }
        logger.debug(f"Placeholders: {placeholders}")

        try:
            output_file = template.format(**placeholders)
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
