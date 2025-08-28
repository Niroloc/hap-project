from abc import ABC, abstractmethod

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.context.context import Context

class MessageFactory(ABC):
    message: str = 'unknown'
    def __init__(self, context: Context):
        self.context = context

    def get_kb(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=k) for k in self.context.button_to_factory]
        buttons = [buttons[i: i + 2] for i in range(0, len(buttons), 2)]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)

    @abstractmethod
    async def callback(self, message: Message) -> None:
        pass


class PaybackMessageFactory(MessageFactory):
    message: str = 'payback'
    async def callback(self, message: Message) -> None:
        builder = InlineKeyboardBuilder()
        self.context.db.get_actual_loans()
