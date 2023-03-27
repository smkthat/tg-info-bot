import asyncio

from app.configuration.log import get_logger

LOGGER = get_logger(__name__, 'logs')


def main():
    try:
        LOGGER.info("start application")
        from app.loader import start_app
        asyncio.run(start_app())
    except (KeyboardInterrupt | SystemExit | AttributeError | FileNotFoundError) as exc:
        LOGGER.error(exc)
        LOGGER.warning("Exit")


if __name__ == "__main__":
    main()
