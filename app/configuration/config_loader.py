import os
import dotenv

from omegaconf import OmegaConf

from app.configuration.log import get_logger

LOGGER = get_logger(__name__, 'logs')
CONFIG_PATH = os.path.relpath('config.yaml')


def check_env_vars():
    """This function checks that the required environment variables are set in the .env file.

    It loads the environment variables from the .env file into the dotenv module
    and checks if all the required variables are present:
     - BOT_TOKEN (str): Telegram bot token
     - DB_USER_PASSWORD (str): (Optional) PostgreSQL user password

    If they are missing, it will print out a message indicating that the required
    variables need to be provided and exit the program.

    For correct implement secret params, see .env.example
    """
    dotenv.load_dotenv()
    required_vars = ['BOT_TOKEN']
    for key, value in dotenv.dotenv_values().items():
        if key in required_vars and not value:
            message = f'Please, provide {key} variable in .env file. See example on .env.template'
            LOGGER.fatal(message)
            exit(message)


def load_configuration():
    LOGGER.debug('load configuration')
    return OmegaConf.load(file_=CONFIG_PATH)


check_env_vars()
CONFIG = load_configuration()
