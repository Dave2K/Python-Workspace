# _modules/logging/logging.py
import datetime
import logging
import sys
import os
from pathlib import Path
from typing import Optional, List

class ColoredFormatter(logging.Formatter):
    """Formattatore avanzato per console con colori ANSI"""
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

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, self.COLORS[logging.INFO])
        formatted = super().format(record)
        return f"{color}{formatted}{self.RESET}"

class LoggingConfigurator:
    """Gestione logging avanzata con funzionalità verificate"""
    
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
        'max_log_files': 7,  # Valore di default più sicuro
        'file_format': "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
        'console_format': "%(asctime)s - %(levelname)-8s - %(message)s",
        'file_level': logging.DEBUG,
        'console_level': logging.INFO
    }

    def __init__(self, **kwargs):
        self.config = {**self.DEFAULT_CONFIG, **self._validate_config(kwargs)}
        self._setup_logging()

    def _validate_config(self, config: dict) -> dict:
        """Validazione dei parametri di configurazione"""
        if config.get('max_log_files') and not isinstance(config['max_log_files'], int):
            raise ValueError("max_log_files deve essere un intero")
        
        if not isinstance(config.get('log_folder', ''), str):
            raise TypeError("log_folder deve essere una stringa")
            
        return config

    def _setup_logging(self) -> None:
        """Configurazione principale del logging"""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.config['log_level'])
        self._clear_handlers(root_logger)

        if self.config['enable_console_logging']:
            self._add_console_handler(root_logger)

        if self.config['enable_file_logging']:
            self._add_file_handler(root_logger)
            self._clean_old_logs()

    def _clear_handlers(self, logger: logging.Logger) -> None:
        """Pulizia completa degli handler esistenti"""
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    def _add_console_handler(self, logger: logging.Logger) -> None:
        """Configurazione output console"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.config['console_level'])
        console_handler.setFormatter(ColoredFormatter(
            fmt=self.config['console_format'],
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(console_handler)

    def _add_file_handler(self, logger: logging.Logger) -> None:
        """Configurazione log su file"""
        log_folder = Path(self.config['log_folder'])
        log_folder.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(
            log_folder / self._generate_log_filename(),
            encoding="utf-8",
            mode="a"
        )
        file_handler.setLevel(self.config['file_level'])
        file_handler.setFormatter(logging.Formatter(
            fmt=self.config['file_format'],
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(file_handler)

    def _generate_log_filename(self) -> str:
        """Generazione nome file con controllo degli errori"""
        try:
            script_name = self.config['script_name_override'] or Path(sys.argv[0]).stem
        except Exception:
            script_name = "unknown_script"

        parts: List[str] = []
        if self.config['file_prefix']:
            parts.append(self.config['file_prefix'])
        
        if self.config['log_name_source']:
            parts.append(script_name)
        
        if self.config['enable_timestamp']:
            parts.append(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        
        filename = "_".join(parts) if parts else "default"
        return f"{filename}.{self.config['file_extension']}"

    def _clean_old_logs(self) -> None:
        """Pulizia automatica con pattern matching migliorato"""
        if not self.config['max_log_files'] or self.config['max_log_files'] <= 0:
            return

        log_folder = Path(self.config['log_folder'])
        pattern = f"{self.config['file_prefix']}*.{self.config['file_extension']}"
        
        log_files = sorted(
            log_folder.glob(pattern),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )

        for old_file in log_files[self.config['max_log_files']:]:
            try:
                old_file.unlink()
            except Exception as e:
                logging.error(f"Errore cancellazione file {old_file}: {str(e)}")

def configure_logging(**kwargs) -> LoggingConfigurator:
    return LoggingConfigurator(**kwargs)

def create_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or __name__)