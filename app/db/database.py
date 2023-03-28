import json
import dotenv

from functools import partial
from typing import Awaitable
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.configuration.config_loader import CONFIG
from app.configuration.log import get_logger
from app.db.models import Base

LOGGER = get_logger(__name__, 'logs/sql')
ENGINE = create_async_engine(
    "postgresql+asyncpg://{username}{password}@{host}:{port}/{db_name}".format(
        username=CONFIG.database.username,
        password=f':{dotenv.dotenv_values()["DB_USER_PASSWORD"]}' if dotenv.dotenv_values()["DB_USER_PASSWORD"] else '',
        host=CONFIG.database.host,
        port=CONFIG.database.port,
        db_name=CONFIG.database.db_name
    ),
    echo=True,
    future=True,
    json_serializer=partial(json.dumps, ensure_ascii=False),
    pool_pre_ping=True
)


async def init_db():
    LOGGER.info('init database')
    async with ENGINE.begin() as conn:
        LOGGER.debug('create engine')
        if CONFIG.database.flush_db:
            LOGGER.warning('flush database')
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> Awaitable:
    return sessionmaker(ENGINE, class_=AsyncSession, expire_on_commit=False)
