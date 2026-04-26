from .core import init_logger, add_custom_logger_level, update_logger_config
from .models import CustomLoggerLevel, LoggerParams
init_logger()
__all__ = ['add_custom_logger_level', 'update_logger_config', 'CustomLoggerLevel', 'LoggerParams']
