import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from utils.db import Db, ROLE

class Tg:
    def __init__(self, token: str, db: Db):
        self.token = token
        self.db = db
        self.bot = Bot(self.token)
        self.dp = Dispatcher()

        @self.dp.message(Command("start"))
        async def start(msg: Message) -> None:
            tg_id = msg.from_user.id
            role = self.db.user_role(tg_id)
            if role == ROLE.NOT_USER:    
                await msg.answer("Для начала работы с проектом необходимо завершить регистрацию через администратора проекта")
                return
            await msg.answer("Добро пожаловать в Проект Хапэрыч!\n" \
                                "Здесь можно оформлять займы из разных источников " \
                                "и получать оперативную отчётность по текущему состоянию " \
                                "проекта за разные периоды времени, а также получать напоминания " \
                                "о необходимости произведения выплат" \
                                "Ваша текущая роль: " + str(role))
        
    async def run(self):
        await self.dp.start_polling(self.bot)
