import datetime
import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
import os

# TURN OFF LOGGING FOR PRODUCTION
logging.disable(logging.CRITICAL)

def log_benchmark(fn, start, end):
    """
    Log a given function and how long the function takes in seconds
    :param str fn: Function name
    :param float start: Function start time
    :param float end: Function end time
    :return none:
    """
    elapsed = round(end - start, 2)
    line = ("Benchmark - Function: {} , Time: {} seconds".format(fn, elapsed))
    return line


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


def create_benchmark(name, log_file, level=logging.INFO):
    """
    Creates a logger for function benchmark times
    :param str name: Name of the logger
    :param str log_file: Filename
    :return obj: Logger
    """
    handler = logging.FileHandler(log_file)
    rtf_handler = RotatingFileHandler(log_file, maxBytes=30000, backupCount=0)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(rtf_handler)
    return logger


def create_logger(name):
    """
    Creates a logger with the below attributes.
    :param str name: Name of the logger
    :return obj: Logger
    """
    # TURNED OFF LOGGING FOR PRODUCTION
    logging.config.dictConfig({'version': 1})
    # logging.config.dictConfig({
    #     'version': 1,
    #     'disable_existing_loggers': True,
    #     'formatters': {
    #         'simple': {
    #             'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    #         },
    #         'detailed': {
    #             'format': '%(asctime)s %(module)-17s line:%(lineno)-4d '
    #                       '%(levelname)-8s %(message)s'
    #         },
    #         'email': {
    #             'format': 'Timestamp: %(asctime)s\nModule: %(module)s\n'
    #                       'Line: %(lineno)d\nMessage: %(message)s'
    #         },
    #     },
    #     'handlers': {
    #         # 'stream': {
    #         #     'level': 'DEBUG',
    #         #     'class': 'logging.StreamHandler',
    #         #     "formatter": "simple"
    #         # },
    #         "file": {
    #             "level": "DEBUG",
    #             "formatter": "simple",
    #             "class": "logging.handlers.RotatingFileHandler",
    #             "filename": "debug.log",
    #             'mode': 'a',
    #             'maxBytes': 30000,
    #             'backupCount': 0
    #         }
    #     },
    #     'loggers': {
    #         '': {
    #             # "handlers": ["stream", "file"],
    #             "handlers": ["file"],
    #             "level": "DEBUG",
    #             'propagate': True
    #         }
    #     }
    # })


    return logging.getLogger(name)

