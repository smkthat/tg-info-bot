from typing import Dict, Any, Optional

from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from sqlalchemy import select, and_
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
            state_data = await self.get_state_data(key)
            state_data.state = state.state if state else None
            state_data.destiny = key.destiny
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

    async def get_state_data(self, key: StorageKey) -> Dict[str, Any]:
        async with self.session() as session:
            try:
                query = select(StateData.data).filter_by(
                    bot_id=key.bot_id,
                    chat_id=key.chat_id,
                    user_id=key.user_id
                )
                res = await session.execute(query)
                state_data = res.scalars().one()
            except NoResultFound:
                state_data = {}
        return state_data

    async def set_data(self, key: StorageKey, data: Dict[str, Any], **kwargs) -> None:
        async with self.session() as session:
            try:
                res = await session.execute(
                    select(StateData).where(and_(
                        StateData.chat_id == key.chat_id,
                        StateData.user_id == key.user_id,
                        StateData.bot_id == key.bot_id
                    )).with_for_update()
                )
                state_data: StateData = res.scalars().one()
                updated_value: dict = state_data.data.copy()
                if not data and key.destiny in state_data.data:
                    updated_value.pop(key.destiny)
                else:
                    updated_value.update({key.destiny: data})
                state_data.data = updated_value
            except NoResultFound:
                state_data = StateData(
                    bot_id=key.bot_id,
                    chat_id=key.chat_id,
                    user_id=key.user_id,
                    data={key.destiny: data}
                )
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
                state_data: StateData = res.scalars().one()
            except NoResultFound:
                return {}

            return state_data.data.get(key.destiny, {})

    async def close(self) -> None:
        await self.engine.dispose()
