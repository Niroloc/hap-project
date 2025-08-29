from abc import ABC, abstractmethod

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.context.context import Context

class MessageFactory(ABC):
    message: str = 'unknown'
    def __init__(self, context: Context):
        self.context = context
        self.step: int = 0
        self.mod: int = 1

    def get_kb(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=k) for k in self.context.BUTTON_TO_FACTORY]
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


class SourceMessageFactory(MessageFactory):
    message: str = 'source'
    def __init__(self, context: Context):
        super().__init__(context=context)
        self.mod = 2

    async def callback(self, message: Message) -> None:
        if self.step == 0:
            await message.answer(text="Введите имя нового источника", reply_markup=self.get_kb())
            self.context.input_mode_message_alias = self.message
        elif self.step == 1:
            if not self.context.db.add_source(message.text):
                await message.answer(text="Что-то при добавлении пошло не так", reply_markup=self.get_kb())
            else:
                await message.answer(text="Источник успешно добавлен", reply_markup=self.get_kb())
            self.context.input_mode_message_alias = None
        self.step += 1
        self.step %= self.mod


class LegendMessageFactory(MessageFactory):
    message: str = 'legend'
    def __init__(self, context: Context):
        super().__init__(context=context)
        self.mod = 2

    async def callback(self, message: Message) -> None:
        if self.step == 0:
            await message.answer(text="Введите имя новой легенды", reply_markup=self.get_kb())
            self.context.input_mode_message_alias = self.message
        elif self.step == 1:
            if not self.context.db.add_legend_source(message.text):
                await message.answer(text="Что-то при добавлении пошло не так", reply_markup=self.get_kb())
            else:
                await message.answer(text="Легенда успешно добавлена", reply_markup=self.get_kb())
            self.context.input_mode_message_alias = None
        self.step += 1
        self.step %= self.mod


class PaybackMessageFactory(MessageFactory):
    message: str = 'payback'
    async def callback(self, message: Message) -> None:
        pass


class LoanMessageFactory(MessageFactory):
    message: str = 'loan'
    async def callback(self, message: Message) -> None:
        pass


class ScheduleMessageFactory(MessageFactory):
    message: str = 'schedule'
    async def callback(self, message: Message) -> None:
        pass


class AnalyticsMessageFactory(MessageFactory):
    message: str = 'analytics'
    async def callback(self, message: Message) -> None:
        pass
