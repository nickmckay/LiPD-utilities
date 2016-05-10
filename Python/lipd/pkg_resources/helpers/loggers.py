import datetime
import logging
from logging.config import dictConfig


def update_changelog():
    """
    Create or update the changelog txt file. Prompt for update description.
    :return None:
    """
    # description = input("Please enter a short description for this update:\n ")
    description = 'Placeholder for description here.'

    # open changelog file for appending. if doesn't exist, creates file.
    with open('changelog.txt', 'a+') as f:
        # write update line
        f.write(str(datetime.datetime.now().strftime("%d %B %Y %I:%M%p")) + '\nDescription: ' + description)
    return


def create_logger(name):
    """
    Creates a logger with the below attributes.
    :param str name: Name of the logger
    :return obj: Logger
    """
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

