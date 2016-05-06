import logging
from logging.config import dictConfig


def create_logger(name):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s %(module)-17s line:%(lineno)-4d '
                          '%(levelname)-8s %(message)s'
            },
            'email': {
                'format': 'Timestamp: %(asctime)s\nModule: %(module)s\n'
                          'Line: %(lineno)d\nMessage: %(message)s'
            },
        },
        'handlers': {
            # 'stream': {
            #     'level': 'DEBUG',
            #     'class': 'logging.StreamHandler',
            #     "formatter": "simple"
            # },
            "file": {
                "level": "DEBUG",
                "formatter": "simple",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "debug.log",
                'mode': 'a',
                'maxBytes': 10485760,
                'backupCount': 3
            }
        },
        'loggers': {
            '': {
                # "handlers": ["stream", "file"],
                "handlers": ["file"],
                "level": "DEBUG",
                'propagate': True
            }
        }
    })
    return logging.getLogger(name)

