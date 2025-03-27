# _modules/logging/logging.py
import datetime
import logging
import sys
import os
from pathlib import Path
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """Formattatore avanzato per console con colori"""
    COLORS = {
        logging.DEBUG: "\x1b[36;20m",    # Ciano
        logging.INFO: "\x1b[32;20m",     # Verde
        logging.WARNING: "\x1b[33;20m",  # Giallo
        logging.ERROR: "\x1b[31;20m",    # Rosso
        logging.CRITICAL: "\x1b[31;1m"   # Rosso intenso
    }
    RESET = "\x1b[0m"

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        fmt = fmt or "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s"
        super().__init__(fmt, datefmt)

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.COLORS[logging.INFO])
        formatted = super().format(record)
        return f"{color}{formatted}{self.RESET}"

class LoggingConfigurator:
    """Gestione logging avanzata con pulizia automatica e output differenziati"""
    
    DEFAULT_CONFIG = {
        'log_folder': "_logs",
        'log_level': logging.INFO,
        'enable_file_logging': True,
        'enable_console_logging': True,
        'log_name_source': True,
        'enable_timestamp': False,
        'file_prefix': "log",
        'file_extension': "log",
        'script_name_override': None,
        'max_log_files': None,          # Numero massimo di file da mantenere
        'file_format': "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
        'console_format': "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
        'file_level': logging.DEBUG,    # Livello diverso per file
        'console_level': logging.INFO   # Livello diverso per console
    }

    def __init__(self, **kwargs):
        self.config = {**self.DEFAULT_CONFIG, **kwargs}
        self._setup_logging()

    def _setup_logging(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(self.config['log_level'])

        # Pulisci handler esistenti
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Configura console
        if self.config['enable_console_logging']:
            self._add_console_handler(root_logger)

        # Configura file
        if self.config['enable_file_logging']:
            self._add_file_handler(root_logger)
            self._clean_old_logs()

    def _add_console_handler(self, logger: logging.Logger):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.config['console_level'])
        console_handler.setFormatter(ColoredFormatter(
            fmt=self.config['console_format'],
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(console_handler)

    def _add_file_handler(self, logger: logging.Logger):
        log_folder = Path(self.config['log_folder'])
        log_folder.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(
            log_folder / self._generate_log_filename(),
            encoding="utf-8"
        )
        file_handler.setLevel(self.config['file_level'])
        file_handler.setFormatter(logging.Formatter(
            fmt=self.config['file_format'],
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(file_handler)

    def _generate_log_filename(self):
        """Genera nome file con regole configurabili"""
        parts = []
        if self.config['file_prefix']:
            parts.append(self.config['file_prefix'])
        
        if self.config['log_name_source']:
            script_name = self.config['script_name_override'] or Path(sys.argv[0]).stem
            parts.append(script_name)
        
        if self.config['enable_timestamp']:
            parts.append(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        
        filename = "_".join(parts) if parts else "log"
        return f"{filename}.{self.config['file_extension']}"

    def _clean_old_logs(self):
        """Pulizia automatica dei log obsoleti"""
        if not self.config['max_log_files']:
            return

        log_folder = Path(self.config['log_folder'])
        pattern = f"*.{self.config['file_extension']}"
        
        # Trova tutti i file di log e ordina per data
        log_files = sorted(
            log_folder.glob(pattern),
            key=os.path.getmtime,
            reverse=True
        )

        # Elimina i file in eccesso
        for old_file in log_files[self.config['max_log_files']:]:
            old_file.unlink()

    @classmethod
    def create_logger(cls, name: str | None = None) -> logging.Logger:
        return logging.getLogger(name or __name__)

# Shortcut functions
def configure_logging(**kwargs) -> LoggingConfigurator:
    return LoggingConfigurator(**kwargs)

create_logger = LoggingConfigurator.create_logger