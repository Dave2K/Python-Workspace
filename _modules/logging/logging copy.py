"""
Modulo di logging avanzato con le seguenti funzionalità:

Funzionalità principali:
- Logging su console con colori ANSI
- Logging su file con rotazione automatica
- Formattazione personalizzabile per console/file
- Supporto multi-livello (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Pulizia automatica dei log obsoleti
- Scelta tra append e sovrascrittura dei file
- Naming file flessibile con timestamp e prefissi

Configurazione base:
from _modules.logging import configure_logging, create_logger
configure_logging()  # Configurazione di default
logger = create_logger(__name__)

# -------------------------------------------------------------------
# ESEMPI DI SETUP CONFIGURAZIONE
# -------------------------------------------------------------------

1. Configurazione Sviluppo (default)
   - Log a colori su console
   - Log dettagliati su file
   - Rotazione automatica (7 file)
dev_config = {
    'log_folder': "dev_logs",
    'file_prefix': "dev"
}


2. Configurazione Produzione
   - Solo log su file
   - Formato semplificato
   - Rotazione giornaliera

prod_config = {
    'enable_console_logging': False,
    'file_format': "%(asctime)s | %(levelname)-8s | %(message)s",
    'enable_timestamp': True,
    'max_log_files': 30,
    'file_prefix': "prod"
}

3. Configurazione Debug
   - Log completi con stack trace
   - Console det
"""

import datetime
import logging
import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

class ColoredFormatter(logging.Formatter):
    """
    Formattatore per console con colori ANSI
    
    Parametri:
    - fmt: Formato del messaggio (default: "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s")
    - datefmt: Formato della data (default: "%Y-%m-%d %H:%M:%S")
    
    Colori disponibili:
    - DEBUG: Ciano
    - INFO: Verde
    - WARNING: Giallo
    - ERROR: Rosso
    - CRITICAL: Rosso intenso
    """
    
    COLORS = {
        logging.DEBUG: '\033[36m',     # Ciano
        logging.INFO: '\033[32m',      # Verde
        logging.WARNING: '\033[33m',   # Giallo
        logging.ERROR: '\033[31m',     # Rosso
        logging.CRITICAL: '\033[31;1m' # Rosso intenso
    }
    RESET = '\033[0m'

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(
            fmt or "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
            datefmt or "%Y-%m-%d %H:%M:%S"
        )

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.COLORS[logging.INFO])
        return f"{color}{super().format(record)}{self.RESET}"

class LoggingConfigurator:
    """
    Configuratore centrale del sistema di logging
    
    Parametri di configurazione:
    
    :param log_folder: Cartella per i log (default: "logs")
    :param log_level: Livello base del logger (default: logging.INFO)
    :param enable_console_logging: Abilita output su console (default: True)
    :param console_level: Livello per la console (default: logging.INFO)
    :param console_format: Formato console (default: "%(asctime)s - %(levelname)-8s - %(message)s")
    :param enable_file_logging: Abilita log su file (default: True)
    :param file_level: Livello per i file (default: logging.DEBUG)
    :param file_format: Formato file (default: "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-20s | %(message)s")
    :param file_prefix: Prefisso nome file (default: "app")
    :param log_name_source: Includi nome script nel nome file (default: True)
    :param script_name_override: Nome script personalizzato (default: None)
    :param enable_timestamp: Aggiungi timestamp al nome file (default: False)
    :param file_extension: Estensione file (default: "log")
    :param max_log_files: Numero massimo file da mantenere (default: 7)
    :param file_mode: Modalità scrittura file ('a'=append, 'w'=sovrascrivi) (default: 'a')
    :param rotate_on_start: Cancella log esistenti all'avvio (solo con file_mode='w') (default: False)
    """
    
    DEFAULTS: Dict[str, Any] = {
        'log_folder': "logs",
        'log_level': logging.INFO,
        'enable_console_logging': True,
        'console_level': logging.INFO,
        'console_format': "%(asctime)s - %(levelname)-8s - %(message)s",
        'enable_file_logging': True,
        'file_level': logging.DEBUG,
        'file_format': "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-20s | %(message)s",
        'file_prefix': "app",
        'log_name_source': True,
        'script_name_override': None,
        'enable_timestamp': False,
        'file_extension': "log",
        'max_log_files': 7,
        'file_mode': 'w',
        'rotate_on_start': False
    }

    def __init__(self, **kwargs):
        self.config = {**self.DEFAULTS, **self._validate_config(kwargs)}
        self._setup()

    def _validate_config(self, config: Dict) -> Dict:
        """Valida i parametri di configurazione"""
        if not isinstance(config.get('log_folder', ''), str):
            raise TypeError("log_folder deve essere una stringa")
        
        if config.get('max_log_files') and not isinstance(config['max_log_files'], int):
            raise ValueError("max_log_files deve essere un intero")
            
        if config.get('file_mode') not in ('a', 'w'):
            raise ValueError("file_mode deve essere 'a' (append) o 'w' (write)")
            
        return config

    def _setup(self) -> None:
        """Configura il sistema di logging"""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.config['log_level'])
        self._clear_handlers(root_logger)

        if self.config['enable_console_logging']:
            self._add_console_handler(root_logger)

        if self.config['enable_file_logging']:
            if self.config['rotate_on_start'] and self.config['file_mode'] == 'w':
                self._clean_old_logs(keep=0)
                
            self._add_file_handler(root_logger)
            self._clean_old_logs()

    def _clear_handlers(self, logger: logging.Logger) -> None:
        """Rimuove tutti gli handler esistenti"""
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    def _add_console_handler(self, logger: logging.Logger) -> None:
        """Aggiunge handler per la console"""
        handler = logging.StreamHandler()
        handler.setLevel(self.config['console_level'])
        handler.setFormatter(ColoredFormatter(
            fmt=self.config['console_format']
        ))
        logger.addHandler(handler)

    def _add_file_handler(self, logger: logging.Logger) -> None:
        """Aggiunge handler per i file"""
        log_file = self._generate_log_filename()
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(
            filename=log_file,
            encoding='utf-8',
            mode=self.config['file_mode']
        )
        handler.setLevel(self.config['file_level'])
        handler.setFormatter(logging.Formatter(
            fmt=self.config['file_format'],
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(handler)

    def _generate_log_filename(self) -> Path:
        """Genera il nome del file di log"""
        try:
            script_name = self.config['script_name_override'] or Path(sys.argv[0]).stem
        except Exception:
            script_name = "unknown"

        parts: List[str] = []
        if self.config['file_prefix']:
            parts.append(self.config['file_prefix'])
        
        if self.config['log_name_source']:
            parts.append(script_name)
        
        if self.config['enable_timestamp']:
            parts.append(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        
        filename = "_".join(parts) or "default"
        return Path(self.config['log_folder']) / f"{filename}.{self.config['file_extension']}"

    def _clean_old_logs(self, keep: Optional[int] = None) -> None:
        """Pulizia automatica dei log"""
        keep = keep or self.config['max_log_files']
        if not keep or keep <= 0:
            return

        pattern = f"{self.config['file_prefix']}*.{self.config['file_extension']}"
        log_files = sorted(
            Path(self.config['log_folder']).glob(pattern),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )

        for old_file in log_files[keep:]:
            try:
                old_file.unlink()
            except Exception as e:
                logging.error(f"Errore cancellazione log: {str(e)}", exc_info=True)

def configure_logging(**kwargs) -> LoggingConfigurator:
    """Configura il sistema di logging
    
    :return: Istanza di LoggingConfigurator
    """
    return LoggingConfigurator(**kwargs)

def create_logger(name: Optional[str] = None) -> logging.Logger:
    """Crea un logger configurato
    
    :param name: Nome del logger (default: nome del modulo corrente)
    :return: Istanza di logging.Logger
    """
    return logging.getLogger(name or __name__)

