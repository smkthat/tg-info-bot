from typing import Dict, Any, Optional

from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from app.configuration.log import get_logger
from app.db.models import StateData

LOGGER = get_logger(__name__, 'logs/sql')


class PostgresStorage(BaseStorage):
    def __init__(self, engine: AsyncEngine):
        self.engine = engine
        self.session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def set_state(self, key: StorageKey, state: StateType = None, **kwargs) -> None:
        async with self.session() as session:
            state_data = await self.__get_state_data(key, session)
            state_data.state = state.state if state else None
            session.add(state_data)
            await session.commit()

    async def get_state(self, key: StorageKey, **kwargs) -> Optional[str]:
        async with self.session() as session:
            try:
                query = select(StateData).filter_by(
                    bot_id=key.bot_id,
                    chat_id=key.chat_id,
                    user_id=key.user_id
                )
                res = await session.execute(query)
                state_data = res.scalars().one()
            except NoResultFound:
                return None

            return state_data.state

    async def __get_state_data(self, key: StorageKey, session: AsyncSession):
        try:
            query = select(StateData).filter_by(
                bot_id=key.bot_id,
                chat_id=key.chat_id,
                user_id=key.user_id
            )
            res = await session.execute(query)
            state_data = res.scalars().one()
        except NoResultFound:
            state_data = StateData(bot_id=key.bot_id, chat_id=key.chat_id, user_id=key.user_id, state=None)
        return state_data

    async def set_data(self, key: StorageKey, data: Dict[str, Any], **kwargs) -> None:
        async with self.session() as session:
            state_data = await self.__get_state_data(key, session)
            state_data.data = data
            session.add(state_data)
            await session.commit()

    async def get_data(self, key: StorageKey, **kwargs) -> Dict[str, Any]:
        async with self.session() as session:
            try:
                query = select(StateData).filter_by(
                    bot_id=key.bot_id,
                    chat_id=key.chat_id,
                    user_id=key.user_id
                )
                res = await session.execute(query)
                state_data = res.scalars().one()
            except NoResultFound:
                return {}

            return state_data.data

    async def close(self) -> None:
        await self.engine.dispose()
