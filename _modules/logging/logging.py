import datetime
import logging
from pathlib import Path

class ColoredFormatter(logging.Formatter):
    """Formattatore per log a colori con codici ANSI"""
    COLORS = {
        logging.DEBUG: "\x1b[36;20m",    # Ciano
        logging.INFO: "\x1b[32;20m",     # Verde
        logging.WARNING: "\x1b[33;20m",  # Giallo
        logging.ERROR: "\x1b[31;20m",    # Rosso
        logging.CRITICAL: "\x1b[31;1m"   # Rosso intenso
    }
    RESET = "\x1b[0m"
    BASE_FORMAT = "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.COLORS[logging.INFO])
        formatter = logging.Formatter(
            f"{color}{self.BASE_FORMAT}{self.RESET}",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        return formatter.format(record)

class LoggingConfigurator:
    """Configurazione centralizzata del sistema di logging"""
    def __init__(self, log_folder="_logs", log_level=logging.INFO, enable_file_logging=True):
        self._setup_logging(
            log_folder=Path(log_folder),
            log_level=log_level,
            enable_file_logging=enable_file_logging
        )

    def _setup_logging(self, log_folder: Path, log_level: int, enable_file_logging: bool):
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Pulizia handler esistenti
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Console handler
        self._add_console_handler(root_logger)

        # File handler
        if enable_file_logging:
            self._add_file_handler(root_logger, log_folder)

    def _add_console_handler(self, logger: logging.Logger):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)

    def _add_file_handler(self, logger: logging.Logger, log_folder: Path):
        log_folder.mkdir(parents=True, exist_ok=True)
        log_file = log_folder / f"dad_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        
        logger.addHandler(file_handler)

    @staticmethod
    def create_logger(name: str | None = None) -> logging.Logger:
        """Restituisce un logger configurato"""
        return logging.getLogger(name)

# Funzioni esportate
def configure_logging(**kwargs) -> LoggingConfigurator:
    """Shortcut per configurazione rapida"""
    return LoggingConfigurator(**kwargs)

create_logger = LoggingConfigurator.create_logger

__all__ = ["LoggingConfigurator", "ColoredFormatter", "configure_logging", "create_logger"]