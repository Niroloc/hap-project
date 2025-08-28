from abc import ABC, abstractmethod

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardButton
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

class InputMessageFactory(MessageFactory):
    message: str = 'ANY'
    async def callback(self, message: Message) -> None:
        await message.answer(text="Значение принято!", reply_markup=self.get_kb())
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Отмена", callback_data=self.context.input_mode_callback_query))
        self.context.input_mode_callback_query.data += "+" + message.text
        builder.row(InlineKeyboardButton(text="Продолжить", callback_data=self.context.input_mode_callback_query))
        await message.answer(text="Продолжить?", reply_markup=builder.as_markup())
        self.context.input_mode_callback_query = None


class PaybackMessageFactory(MessageFactory):
    message: str = 'payback'
    async def callback(self, message: Message) -> None:
        builder = InlineKeyboardBuilder()
        self.context.db.get_actual_loans()

