from app.configuration.config_loader import CONFIG
from app.configuration.log import get_logger

LOGGER = get_logger(__name__, 'logs')


async def start_app():
    if CONFIG:
        LOGGER.info('Done!')
