from .logging_configurator import LoggingConfigurator, ColoredFormatter

__all__ = [
    "LoggingConfigurator",
    "ColoredFormatter",
    "configure_logging",
    "create_logger"
]

def configure_logging(**kwargs) -> LoggingConfigurator:
    """Shortcut per configurazione rapida"""
    return LoggingConfigurator(**kwargs)

create_logger = LoggingConfigurator.create_logger