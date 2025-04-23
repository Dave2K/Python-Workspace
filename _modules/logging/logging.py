"""
Modulo di configurazione avanzata del logging

Questo modulo implementa un sistema di logging avanzato con le seguenti caratteristiche:
- Supporto per un livello di log personalizzato TRACE (livello numerico 5).
- Logging su console con supporto a colori ANSI e icone, con possibilità di personalizzare lo stile:
    - "text": mostra solo il nome del livello.
    - "icon": mostra solo l'icona corrispondente.
    - "both": mostra sia l'icona e il nome del livello.
- Logging su file con formati personalizzati, incluso il supporto per la rotazione automatica dei log.
- Possibilità di specificare formati di log differenti per ciascun livello (ad es. default, info, debug, ecc.).
- Configurazione tramite parametri predefiniti (DEFAULTS) che possono essere sovrascritti tramite argomenti.

Parametri principali (con valori di default e alternative commentate):
- log_folder: Cartella dove vengono salvati i log.
    * Default: "logs"
    * Alternativa: "_logs"
- log_level: Livello di log predefinito (es. logging.DEBUG, logging.INFO, ecc.).
    * Default: logging.DEBUG
- enable_console_logging: Abilita il logging sulla console.
    * Default: True
- console_level: Livello di log per la console.
    * Default: logging.DEBUG
- console_format: Dizionario dei formati per la console per ciascun livello.
    * Default:
          {
              'default': "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
              'info': "%(asctime)s - %(name)s - %(message)s",
              'debug': "%(asctime)s - %(levelname)-8s - %(message)s",
          }
- console_style: Stile di visualizzazione per la console ("text", "icon", "both").
    * Default: "text" oppure "both" se si vuole mostrare icona e testo.
- enable_file_logging: Abilita il logging su file.
    * Default: False
- file_level: Livello di log per i file.
    * Default: logging.DEBUG
- file_format: Formato per i log su file.
    * Default: "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-20s | %(message)s"
- file_prefix: Prefisso per il nome dei file di log (se log_name_source=False).
    * Default: "app"
- log_name_source: Se True, usa il nome dello script come prefisso, altrimenti file_prefix.
    * Default: True
- script_name_override: Sovrascrive il nome dello script se fornito.
    * Default: None
- enable_timestamp: Se True, aggiunge date+ora (YYYY-MM-DD_HHMMSS) al nome del file, altrimenti solo data (YYYY-MM-DD).
    * Default: False
- file_extension: Estensione dei file di log.
    * Default: "log"
- max_log_files: Numero massimo di file di log da mantenere.
    * Default: 7
- file_mode: Modalità di apertura del file ("w" per write, "a" per append).
    * Default: "w"
- rotate_on_start: Se True, ruota (cancella) i vecchi log all'avvio se file_mode=='w'.
    * Default: False

Esempio di utilizzo:
--------------------
config = configure_logging(
    enable_file_logging=True,
    file_mode='a',
    log_folder="_logs",
    log_level=logging.DEBUG,
    enable_console_logging=True,
    console_level=logging.DEBUG,
    console_format={
        'default': "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
        'info': "%(asctime)s - %(name)s - %(message)s",
        'debug': "%(asctime)s - %(levelname)-8s - %(message)s",
    },
    console_style="both"
)
logger = create_logger("TestLogger")
logger.info("Messaggio di log di info")
logger.trace("Messaggio di log TRACE (livello personalizzato)")
"""

import colorama
colorama.init()

import datetime
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Definizione del livello TRACE
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")

def trace(self, message, *args, **kwargs):
    """
    Metodo per il logging TRACE.
    Permette di loggare messaggi a livello TRACE, un livello personalizzato inferiore a DEBUG.
    """
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kwargs)

logging.Logger.trace = trace

# Definizione del livello SUCCESS
SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

def success(self, message, *args, **kwargs):
    """
    Metodo per il logging SUCCESS.
    """
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)

logging.Logger.success = success

class ColoredFormatter(logging.Formatter):
    """
    Formattatore personalizzato per la console con supporto a colori ANSI e icone.

    Consente di personalizzare il formato dei messaggi di log in base al livello e di aggiungere
    colori ed icone.

    Attributi:
      COLORS (dict): Mappa dei livelli di log ai codici colore ANSI.
      ICONS (dict): Mappa dei livelli di log alle icone Unicode.
      RESET (str): Sequenza ANSI per resettare il colore.
    """

    COLORS = {
        TRACE_LEVEL: '\033[90m',        # Grigio
        SUCCESS_LEVEL: '\033[32m',      # Verde
        logging.DEBUG: '\033[97m',      # Bianco
        logging.INFO: '\033[36m',       # Ciano
        logging.WARNING: '\033[33m',    # Giallo
        logging.ERROR: '\033[31m',      # Rosso
        logging.CRITICAL: '\033[31;1m'  # Rosso intenso
    }
    RESET = '\033[0m'

    ICONS = {
        TRACE_LEVEL: "🔍 ",
        logging.DEBUG: "🛠️ ",
        logging.INFO: ": ℹ️ ",
        logging.WARNING: "⚠️ ",
        logging.ERROR: "❌ ",
        logging.CRITICAL: "🚨 ",
        SUCCESS_LEVEL: "✅ "
    }

    def __init__(self, fmt: Optional[Dict[str, str]] = None, datefmt: Optional[str] = None, style: str = "text"):
        """
        :param fmt: Dizionario che mappa i nomi dei livelli (in minuscolo) ai formati personalizzati.
        :param datefmt: Formato della data per il campo asctime.
        :param style: Stile di visualizzazione per il livello ("text", "icon", "both").
        """
        default_fmt = "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s"
        super().__init__(fmt=fmt.get('default', default_fmt) if fmt else default_fmt,
                         datefmt=datefmt or "%Y-%m-%d %H:%M:%S")
        self.style = style
        self.formats = fmt or {}

    def format(self, record: logging.LogRecord) -> str:
        """
        Applica la formattazione personalizzata al record, aggiungendo colori ed icone.

        Costruisce il messaggio una sola volta utilizzando il formato scelto, senza duplicazioni.
        """
        record.asctime = self.formatTime(record, self.datefmt)
        orig_level = record.levelname
        level_format = self.formats.get(orig_level.lower(), self.formats.get('default'))

        if self.style == "icon":
            level_display = self.ICONS.get(record.levelno, "")
        elif self.style == "both":
            level_display = f"{self.ICONS.get(record.levelno, '')} {orig_level}"
        else:
            level_display = orig_level

        record.levelname = level_display
        record.__dict__['message'] = record.getMessage()
        message = level_format % record.__dict__
        return f"{self.COLORS.get(record.levelno, self.COLORS[logging.INFO])}{message}{self.RESET}"

class LoggingConfigurator:
    """
    Configuratore avanzato del sistema di logging.

    Configura il logging per console e file, con formati personalizzati per ciascun livello,
    e supporta opzioni come la rotazione dei file.
    """

    DEFAULTS: Dict[str, Any] = {
        'log_folder': "logs",
        'log_level': logging.INFO,
        'enable_console_logging': True,
        'console_level': logging.DEBUG,
        'console_format': {
            'default': "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
            'info': "%(asctime)s - %(name)s - %(message)s",
            'debug': "%(asctime)s - %(levelname)-8s - %(message)s",
        },
        'console_style': "text",
        'enable_file_logging': False,
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
        """
        Inizializza e configura il sistema di logging con i parametri forniti.

        :param kwargs: Parametri di configurazione che sovrascrivono i valori di default.
        """
        self.config = self._validate_config({**self.DEFAULTS, **kwargs})
        self._setup()

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida i parametri di configurazione.
        :raises: TypeError o ValueError se i parametri non sono conformi.
        """
        if not isinstance(config['log_folder'], str):
            raise TypeError("log_folder deve essere una stringa")
        if not isinstance(config['max_log_files'], int) or config['max_log_files'] < 0:
            raise ValueError("max_log_files deve essere un intero positivo o 0")
        if config['file_mode'] not in ('a', 'w'):
            raise ValueError("file_mode deve essere 'a' (append) o 'w' (write')")
        if config['console_style'] not in ("text", "icon", "both"):
            raise ValueError("console_style deve essere 'text', 'icon' o 'both'")
        return config

    def _setup(self) -> None:
        """
        Configura il logging, impostando i gestori per console e file (se abilitati)
        e rimuovendo eventuali handler esistenti.
        """
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
        """
        Rimuove tutti gli handler esistenti dal logger.
        """
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    def _add_console_handler(self, logger: logging.Logger) -> None:
        """
        Aggiunge un handler per la console, configurato con il livello e il formato personalizzato.
        """
        console_level = self.config.get('console_level', self.config['log_level'])
        logger.setLevel(min(self.config['log_level'], console_level))
        handler = logging.StreamHandler()
        handler.setLevel(console_level)
        handler.setFormatter(ColoredFormatter(fmt=self.config['console_format'],
                                            style=self.config['console_style']))
        logger.addHandler(handler)

    def _add_file_handler(self, logger: logging.Logger) -> None:
        """
        Aggiunge un handler per il file di log, configurato con il livello e il formato specificato.
        """
        log_file = self._generate_log_filename()
        handler = logging.FileHandler(filename=log_file,
                                      encoding='utf-8',
                                      mode=self.config['file_mode'])
        handler.setLevel(self.config['file_level'])
        handler.setFormatter(logging.Formatter(fmt=self.config['file_format'],
                                               datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)

    def _generate_log_filename(self) -> Path:
        """
        Genera il nome del file di log in base alla configurazione:
        - Usa il nome dello script (o script_name_override) se log_name_source=True, altrimenti file_prefix.
        - Aggiunge data o data+ora in base a enable_timestamp.
        - Imposta estensione da file_extension.
        """
        folder = Path(self.config['log_folder'])
        folder.mkdir(parents=True, exist_ok=True)

        if self.config['log_name_source']:
            base = Path(self.config['script_name_override'] or sys.argv[0]).stem
        else:
            base = self.config['file_prefix']

        if self.config['enable_timestamp']:
            stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        else:
            stamp = datetime.datetime.now().strftime("%Y-%m-%d")

        ext = self.config.get('file_extension', 'log')
        filename = f"{base}_{stamp}.{ext}"
        return folder / filename

    def _clean_old_logs(self, keep: int = None) -> None:
        """
        Pulisce i file di log più vecchi, mantenendo al massimo 'keep' file
        (o self.config['max_log_files'] se keep è None).
        """
        log_folder = Path(self.config['log_folder'])
        ext = self.config.get('file_extension', 'log')
        max_keep = keep if keep is not None else self.config['max_log_files']

        all_logs = sorted(
            log_folder.glob(f"*.{ext}"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        for old_file in all_logs[max_keep:]:
            try:
                old_file.unlink()
            except Exception:
                pass

def configure_logging(**kwargs) -> LoggingConfigurator:
    """
    Funzione helper per configurare il sistema di logging.
    """
    return LoggingConfigurator(**kwargs)

def create_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Crea e restituisce un logger configurato.
    """
    return logging.getLogger(name or __name__)
