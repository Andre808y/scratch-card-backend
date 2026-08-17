"""Каркас aiogram-бота и диспетчера."""

import asyncio

from aiogram import Bot, Dispatcher

from src.bot.handlers.play import router as play_router
from src.config import settings
from src.logging_config import configure_logging


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(play_router)
    return dispatcher


async def run() -> None:
    configure_logging()
    bot = Bot(token=settings.bot_token)
    dispatcher = create_dispatcher()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run())
