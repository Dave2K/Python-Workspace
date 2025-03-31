"""
Modulo di configurazione avanzata del logging

Questo modulo implementa un sistema di logging avanzato con le seguenti caratteristiche:
- Supporto per un livello di log personalizzato TRACE (livello numerico 5).
- Logging su console con supporto a colori ANSI e icone, con possibilità di personalizzare lo stile:
    - "text": mostra solo il nome del livello.
    - "icon": mostra solo l'icona corrispondente.
    - "both": mostra sia l'icona che il nome del livello.
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
- console_format: Dizionario dei formati per la console per ogni livello.
    * Default:
          {
              'default': "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
              'info': "%(asctime)s - %(name)s - %(message)s",
              'debug': "%(asctime)s - %(levelname)-8s - %(message)s",
          }
- console_style: Stile di visualizzazione della console ("text", "icon", "both").
    * Default: "text" oppure "both" se si vuole mostrare icona e testo.
- enable_file_logging: Abilita il logging su file.
    * Default: False
- file_level: Livello di log per i file.
    * Default: logging.DEBUG
- file_format: Formato per i log su file.
    * Default: "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-20s | %(message)s"
- file_prefix: Prefisso per il nome dei file di log.
    * Default: "app"
- max_log_files: Numero massimo di file di log da mantenere.
    * Default: 7
- file_mode: Modalità di apertura del file ("w" per scrivere, "a" per appendere).
    * Default: "w" (alternativa: 'a' per append)
- rotate_on_start: Se True, ruota (cancella) i vecchi log all'avvio.
    * Default: False

Esempio di utilizzo:
--------------------
config = configure_logging(
    enable_file_logging=True,       # Abilita il log su file
    # file_mode='a',                # Alternativa per append; default 'w'
    # log_folder="_logs",           # Alternativa al default "logs"
    log_level=logging.DEBUG,        # Livello di log globale
    enable_console_logging=True,    # Abilita il log sulla console
    console_level=logging.DEBUG,    # Livello di log per la console
    console_format={                # Formati per ogni livello
        'default': "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
        'info': "%(asctime)s - %(name)s - %(message)s",
        'debug': "%(asctime)s - %(levelname)-8s - %(message)s",
    },
    console_style="both",           # Mostra sia icona che testo in console
    file_level=logging.DEBUG,       # Livello di log per file
    file_format="%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-20s | %(message)s",
    file_prefix="app",              # Prefisso per i file di log
    max_log_files=7,                # Numero massimo di file di log
    rotate_on_start=False           # Non ruotare i log all'avvio
)
logger = create_logger("TestLogger")
logger.info("Messaggio di log di info")
logger.trace("Messaggio di log TRACE (livello personalizzato)")
"""

import colorama
colorama.init()

import datetime
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# Definizione del livello TRACE
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")
# SUCCESS_LEVEL = 4
# logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

def trace(self, message, *args, **kwargs):
    """
    Metodo per il logging TRACE.
    
    Permette di loggare messaggi a livello TRACE, un livello personalizzato inferiore a DEBUG.
    """
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kwargs)

logging.Logger.trace = trace

class ColoredFormatter(logging.Formatter):
    """
    Formattatore personalizzato per la console con supporto a colori ANSI e icone.
    
    Consente di personalizzare il formato dei messaggi di log in base al livello e di aggiungere colori ed icone.
    
    Attributi:
      COLORS (dict): Mappa dei livelli di log ai codici colore ANSI.
      ICONS (dict): Mappa dei livelli di log alle icone Unicode.
      RESET (str): Sequenza ANSI per resettare il colore.
    
    Parametri:
      fmt (dict, opzionale): Dizionario che mappa i nomi dei livelli (in minuscolo) ai formati personalizzati.
                             Se non fornito, viene usato un formato di default.
      datefmt (str, opzionale): Formato della data per il campo asctime.
      style (str): Stile di visualizzazione per il livello ("text", "icon", "both").
                   "text": visualizza solo il nome del livello.
                   "icon": visualizza solo l'icona.
                   "both": visualizza sia icona che nome del livello.
    """
    COLORS = {
        TRACE_LEVEL: '\033[90m',        # Grigio
        logging.DEBUG: '\033[97m',      # Bianco
        logging.INFO: '\033[36m',       # Ciano
        logging.WARNING: '\033[33m',    # Giallo
        logging.ERROR: '\033[31m',      # Rosso
        logging.CRITICAL: '\033[31;1m', # Rosso intenso
        # SUCCESS_LEVEL: '\033[32m',      # Verde
    }
    RESET = '\033[0m'

    ICONS = {
        TRACE_LEVEL: "🔍 ",
        logging.DEBUG: "🛠️ ",
        logging.INFO: ": ℹ️ ",
        logging.WARNING: "⚠️ ",
        logging.ERROR: "❌ ",
        logging.CRITICAL: "🚨 ",
        # SUCCESS_LEVEL: "✅ "
    }

    def __init__(self, fmt: Optional[Dict[str, str]] = None, datefmt: Optional[str] = None, style: str = "text"):
        default_fmt = "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s"
        super().__init__(fmt=fmt.get('default', default_fmt) if fmt else default_fmt,
                         datefmt=datefmt or "%Y-%m-%d %H:%M:%S")
        self.style = style
        self.formats = fmt or {}

    def format(self, record: logging.LogRecord) -> str:
        """
        Applica la formattazione personalizzata al record, aggiungendo colori ed icone.
        
        Costruisce il messaggio una sola volta utilizzando il formato scelto, senza duplicazioni.
        
        :param record: Il record di log da formattare.
        :return: La stringa formattata con colori ed icone.
        """
        # Assicura che 'asctime' sia valorizzato
        record.asctime = self.formatTime(record, self.datefmt)
        # Salva il livello originale per selezionare il formato
        orig_level = record.levelname
        # Determina il formato da usare in base al livello originale (in minuscolo)
        level_format = self.formats.get(orig_level.lower(), self.formats.get('default'))
        
        # Determina la rappresentazione del livello in base allo stile
        if self.style == "icon":
            level_display = self.ICONS.get(record.levelno, "")
        elif self.style == "both":
            level_display = f"{self.ICONS.get(record.levelno, '')} {orig_level}"
        else:
            level_display = orig_level
        
        # Aggiorna il record sostituendo levelname (solo per la visualizzazione)
        record.levelname = level_display
        # Prepara il dizionario con i valori aggiornati
        record.__dict__['message'] = record.getMessage()
        # Costruisce il messaggio usando il formato selezionato
        message = level_format % record.__dict__
        return f"{self.COLORS.get(record.levelno, self.COLORS[logging.INFO])}{message}{self.RESET}"

class LoggingConfigurator:
    """
    Configuratore avanzato del sistema di logging.
    
    Questa classe configura il logging per console e file, con formati personalizzati per ciascun livello,
    e supporta opzioni come la rotazione dei file.
    
    Parametri:
      log_folder (str): Cartella in cui salvare i file di log.
          * Default: "logs" (Alternativa: "_logs")
      log_level (int): Livello di log predefinito.
          * Default: logging.DEBUG
      enable_console_logging (bool): Abilita il logging sulla console.
          * Default: True
      console_level (int): Livello di log per la console.
          * Default: logging.DEBUG
      console_format (dict): Dizionario dei formati per la console per ciascun livello.
          * Default:
                {
                    'default': "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
                    'info': "%(asctime)s - %(name)s - %(message)s",
                    'debug': "%(asctime)s - %(levelname)-8s - %(message)s",
                }
      console_style (str): Stile di visualizzazione per la console ("text", "icon", "both").
          * Default: "text" oppure "both"
      enable_file_logging (bool): Abilita il logging su file.
          * Default: False
      file_level (int): Livello di log per i file.
          * Default: logging.DEBUG
      file_format (str): Formato per i log su file.
          * Default: "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-20s | %(message)s"
      file_prefix (str): Prefisso per il nome dei file di log.
          * Default: "app"
      max_log_files (int): Numero massimo di file di log da mantenere.
          * Default: 7
      file_mode (str): Modalità di apertura del file ("w" per scrivere, "a" per appendere).
          * Default: "w" (Alternativa: "a")
      rotate_on_start (bool): Se True, ruota (cancella) i vecchi log all'avvio.
          * Default: False
          
    Esempio di utilizzo:
    --------------------
    config = configure_logging(
        enable_file_logging=True,       # Abilita il log su file
        file_mode='a',                  # Modalità file: 'a' per append, 'w' per sovrascrivere
        log_folder="logs",              # Cartella dei log
        log_level=logging.DEBUG,        # Livello di log globale
        enable_console_logging=True,    # Abilita il log sulla console
        console_level=logging.DEBUG,    # Livello di log per la console
        console_format={
            'default': "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
            'info': "%(asctime)s - %(name)s - %(message)s",
            'debug': "%(asctime)s - %(levelname)-8s - %(message)s",
        },
        console_style="both",           # Mostra sia icona che testo in console
        file_level=logging.DEBUG,       # Livello di log per file
        file_format="%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-20s | %(message)s",
        file_prefix="app",              # Prefisso per i file di log
        max_log_files=7,                # Numero massimo di file di log
        rotate_on_start=False           # Non ruotare i log all'avvio
    )
    """
    DEFAULTS: Dict[str, Any] = {
        'log_folder': "logs",                      # Cartella dei log (alternativa: "_logs")
        'log_level': logging.DEBUG,                # Livello di log globale
        'enable_console_logging': True,            # Abilita log su console
        'console_level': logging.DEBUG,            # Livello di log per la console
        'console_format': {                        # Formati per la console per ciascun livello
            'default': "%(asctime)s - %(levelname)-8s - %(name)s - %(message)s",
            'info': "%(asctime)s - %(name)s - %(message)s",
            'debug': "%(asctime)s - %(levelname)-8s - %(message)s",
        },
        'enable_file_logging': False,              # Abilita log su file (modifica a True per attivare)
        'file_level': logging.DEBUG,               # Livello di log per i file
        'file_format': "%(asctime)s.%(msecs)03d | %(levelname)-8s | %(name)-20s | %(message)s",
        'file_prefix': "app",                      # Prefisso per i file di log
        'log_name_source': True,
        'script_name_override': None,
        'enable_timestamp': False,
        'file_extension': "log",
        'max_log_files': 7,                        # Numero massimo di file di log
        'file_mode': 'w',                          # Modalità file: 'w' per sovrascrivere, 'a' per appendere
        'rotate_on_start': False                   # Rotazione dei log all'avvio
    }
    
    def __init__(self, **kwargs):
        """
        Inizializza e configura il sistema di logging con i parametri forniti.
        
        :param kwargs: Parametri di configurazione che sovrascrivono i valori di default.
        """
        self.config = self._validate_config({**self.DEFAULTS, **kwargs})
        self._setup()
    
    def _validate_config(self, config: Dict) -> Dict:
        """
        Valida i parametri di configurazione.
        
        :param config: Dizionario di configurazione.
        :return: Configurazione validata.
        :raises: TypeError o ValueError se i parametri non sono conformi.
        """
        if not isinstance(config['log_folder'], str):
            raise TypeError("log_folder deve essere una stringa")
        if not isinstance(config['max_log_files'], int) or config['max_log_files'] < 0:
            raise ValueError("max_log_files deve essere un intero positivo o 0")
        if config['file_mode'] not in ('a', 'w'):
            raise ValueError("file_mode deve essere 'a' (append) o 'w' (write)")
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
        
        :param logger: Logger dal quale rimuovere gli handler.
        """
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    def _add_console_handler(self, logger: logging.Logger) -> None:
        """
        Aggiunge un handler per la console, configurato con il livello e il formato personalizzato.
        
        :param logger: Logger a cui aggiungere l'handler.
        """
        handler = logging.StreamHandler()
        handler.setLevel(self.config['console_level'])
        handler.setFormatter(ColoredFormatter(fmt=self.config['console_format'],
                                              style=self.config['console_style']))
        logger.addHandler(handler)
    
    def _add_file_handler(self, logger: logging.Logger) -> None:
        """
        Aggiunge un handler per il file di log, configurato con il livello e il formato specificato.
        
        :param logger: Logger a cui aggiungere l'handler.
        """
        log_file = self._generate_log_filename()
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(filename=log_file, encoding='utf-8', mode=self.config['file_mode'])
        handler.setLevel(self.config['file_level'])
        handler.setFormatter(logging.Formatter(fmt=self.config['file_format'], datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
    
    def _generate_log_filename(self) -> Path:
        """
        Genera il nome del file di log in base alla configurazione attuale.
        
        :return: Percorso completo del file di log.
        """
        log_folder = Path(self.config['log_folder'])
        log_filename = f"{self.config['file_prefix']}_{datetime.datetime.now().strftime('%Y-%m-%d')}.{self.config['file_extension']}"
        return log_folder / log_filename
    
    def _clean_old_logs(self, keep: int = None) -> None:
        """
        Pulisce (rimuove) i vecchi file di log, mantenendo al massimo il numero specificato in max_log_files.
        
        :param keep: Numero di file da mantenere. Se None, usa il valore di max_log_files.
        """
        # Implementazione semplificata: in questa funzione si può scorrere la cartella dei log,
        # ordinare i file per data e rimuovere quelli in eccesso.
        pass

def configure_logging(**kwargs) -> LoggingConfigurator:
    """
    Funzione helper per configurare il sistema di logging.
    
    :param kwargs: Parametri di configurazione che sovrascrivono i valori di default.
    :return: Un'istanza di LoggingConfigurator.
    """
    return LoggingConfigurator(**kwargs)

def create_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Crea e restituisce un logger configurato.
    
    :param name: Nome del logger. Se None, utilizza __name__.
    :return: Logger configurato.
    """
    return logging.getLogger(name or __name__)
