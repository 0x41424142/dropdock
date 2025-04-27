import logging
import logging.config
import logging.handlers  # Import the handlers module
import os
import json
from datetime import datetime

class CustomJsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for logging.
    """
    def format(self, record):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'name': record.name,
            'module': record.module,
            'lineno': record.lineno,
        }
        return json.dumps(log_entry)

def setup_logging():
    """
    Sets up the logging configuration with log rotation.
    """
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_file = os.getenv('LOG_FILE', 'dropdock.log')
    max_bytes = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB default
    backup_count = int(os.getenv('LOG_BACKUP_COUNT', 5))   # Keep 5 backup files by default
    
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': CustomJsonFormatter,
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'json',
                'level': log_level,
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',  # Changed to RotatingFileHandler
                'filename': log_file,
                'formatter': 'json',
                'level': log_level,
                'maxBytes': max_bytes,  # Maximum size before rotation
                'backupCount': backup_count,  # Number of backup files to keep
            },
        },
        'loggers': {
            'dropdock': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False,
            },
        },
    }
    
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger('dropdock')
    logger.info("Logging setup complete with rotation enabled.")
    return logger