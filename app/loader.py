from datetime import datetime, timezone

import dotenv
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import SimpleEventIsolation

from app.configuration.config_loader import CONFIG
from app.configuration.log import get_logger, LOG_DATE_FORMAT
from app.db.database import init_db, ENGINE
from app.db.fsm.storage import PostgresStorage

LOGGER = get_logger(__name__, 'logs')


async def on_startup(bot: Bot):
    if bot_user := await bot.get_me():
        date = datetime.now(timezone.utc).strftime(LOG_DATE_FORMAT)
        await bot.send_message(
            chat_id=CONFIG.bot.owner,
            text=f'{bot_user.mention_markdown()} started at {date}'
        )


async def start_app():
    await init_db()
    dp = Dispatcher(
        events_isolation=SimpleEventIsolation(),
        storage=PostgresStorage(engine=ENGINE)
    )
    bot = Bot(token=dotenv.dotenv_values()['BOT_TOKEN'], parse_mode='markdown')
    dp.startup.register(on_startup)
    await bot.get_updates(offset=-1)
    await dp.start_polling(bot)
