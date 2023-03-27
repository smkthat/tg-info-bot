import logging
import os.path
from datetime import datetime

APP_NAME = os.path.basename(os.getcwd())
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FORMAT = f'%(asctime)s.%(msecs)-3d - {APP_NAME} - %(levelname)-8s -' \
             ' %(name)s.%(funcName)s(line%(lineno)d): %(message)s'

logging.basicConfig(
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    level=logging.DEBUG
)
logFileFormatter = logging.Formatter(
    fmt=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
)

date_now = datetime.utcnow().date()


def create_folders(path: str):
    os.makedirs(path, exist_ok=True)


def get_error_handler(path: str):
    error_handler = logging.FileHandler(filename=f'{path}/{date_now.year}-{date_now.month}-errors.log',
                                        encoding='utf-8')
    error_handler.setFormatter(logFileFormatter)
    error_handler.setLevel(level=logging.ERROR)
    return error_handler


def get_runtime_handler(path: str):
    runtime_handler = logging.FileHandler(
        filename=f'{path}/{date_now.year}-{date_now.month}-runtime.log', encoding='utf-8')
    runtime_handler.setFormatter(logFileFormatter)
    runtime_handler.setLevel(level=logging.DEBUG)
    return runtime_handler


def get_sqlalchemy_handler(path: str):
    sqlalchemy_handler = logging.FileHandler(filename=f'{path}/{date_now.year}-{date_now.month}-sql.log',
                                             encoding='utf-8')
    sqlalchemy_handler.setFormatter(logFileFormatter)
    sqlalchemy_handler.setLevel(level=logging.DEBUG)
    return sqlalchemy_handler


logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine.Engine').propagate = False
logging.getLogger('sqlalchemy.engine.Engine').addHandler(get_sqlalchemy_handler('logs'))


def get_logger(name: str, path: str) -> logging.Logger:
    """Function implement configuration and get new logger

    Arguments:
        name (str): Logger name
        path (str): Path to log file
    Return:
        Configured logger
    """
    create_folders(path)
    logger = logging.getLogger(name)
    logger.addHandler(get_error_handler(path))
    logger.addHandler(get_runtime_handler(path))
    return logger
