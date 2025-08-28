import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from src.bot.factory_helper import CallbackHelper
from src.context.context import Context


class HaperychBot:
    def __init__(self, context: Context):
        self.context = context
        self.helper = CallbackHelper(context)
        self.dp = Dispatcher()
        self.bot = Bot(token=context.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        @self.dp.message(CommandStart())
        async def command_start_handler(message: Message) -> None:
            logging.info(f"Message from {message.chat.id}")
            if not self.check_rights(message):
                return
            await self.helper.default_message_factory.callback(message)

        @self.dp.message()
        async def message_handler(message: Message) -> None:
            if not self.check_rights(message):
                return
            f = self.helper.get_message_callback(message.text)
            if f is not None:
                await f(message)

        @self.dp.callback_query()
        async def callback_handler(callback: CallbackQuery):
            if not self.check_rights(callback.message):
                return
            f = self.helper.get_callback_factory(callback.callback_data).callback
            if f is not None:
                await f(callback)

    def check_rights(self, msg: Message) -> bool:
        return msg.chat.id == self.context.ADMIN_ID

    def run(self):
        asyncio.run(self.dp.start_polling(self.bot))
