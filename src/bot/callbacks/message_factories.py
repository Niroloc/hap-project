from abc import ABC, abstractmethod

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.context.context import Context
from src.utils.utils import encode

class MessageFactory(ABC):
    alias: str = 'unknown'
    def __init__(self, context: Context):
        self.context = context
        self.step: int = 0
        self.mod: int = 1

    def get_kb(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=k) for k in self.context.BUTTON_TO_ALIAS]
        buttons = [buttons[i: i + 2] for i in range(0, len(buttons), 2)]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)

    @abstractmethod
    async def callback(self, message: Message) -> None:
        pass

class InputMessageFactory(MessageFactory):
    alias: str = 'ANY'
    async def callback(self, message: Message) -> None:
        await message.answer(text="Значение принято!", reply_markup=self.get_kb())
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Отмена", callback_data=self.context.input_mode_callback_data))
        self.context.input_mode_callback_data += "_" + encode(message.text)
        builder.row(InlineKeyboardButton(text="Продолжить", callback_data=self.context.input_mode_callback_data))
        await message.answer(text="Продолжить?", reply_markup=builder.as_markup())
        self.context.input_mode_callback_data = None


class SourceMessageFactory(MessageFactory):
    alias: str = 'source'
    def __init__(self, context: Context):
        super().__init__(context=context)
        self.mod = 2

    async def callback(self, message: Message) -> None:
        if self.step == 0:
            await message.answer(text="Введите имя нового источника", reply_markup=self.get_kb())
            self.context.input_mode_message_alias = self.alias
        elif self.step == 1:
            if not self.context.db.add_source(message.text):
                await message.answer(text="Что-то при добавлении пошло не так", reply_markup=self.get_kb())
            else:
                await message.answer(text="Источник успешно добавлен", reply_markup=self.get_kb())
            self.context.input_mode_message_alias = None
        self.step += 1
        self.step %= self.mod


class LegendMessageFactory(MessageFactory):
    alias: str = 'legend'
    def __init__(self, context: Context):
        super().__init__(context=context)
        self.mod = 2

    async def callback(self, message: Message) -> None:
        if self.step == 0:
            await message.answer(text="Введите имя новой легенды", reply_markup=self.get_kb())
            self.context.input_mode_message_alias = self.alias
        elif self.step == 1:
            if not self.context.db.add_legend_source(message.text):
                await message.answer(text="Что-то при добавлении пошло не так", reply_markup=self.get_kb())
            else:
                await message.answer(text="Легенда успешно добавлена", reply_markup=self.get_kb())
            self.context.input_mode_message_alias = None
        self.step += 1
        self.step %= self.mod


class PaybackMessageFactory(MessageFactory):
    alias: str = 'payback'
    async def callback(self, message: Message) -> None:
        builder = InlineKeyboardBuilder()
        buttons = [InlineKeyboardButton(
            text=f"{total} ({legend_name}) до {expected_settle_date.strftime('%d.%m')}",
            callback_data=f"payback_{loan_id}"
        )
            for loan_id, source_id, source_name, loan_date, expected_settle_date,
            amount, total, legend_id, legend_name, comment in self.context.db.get_unsettled_loans()]
        for but in buttons:
            builder.row(but)
        await message.answer(text="Выберите займ для погашения", reply_markup=builder.as_markup())


class LoanMessageFactory(MessageFactory):
    alias: str = 'loan'
    async def callback(self, message: Message) -> None:
        builder = InlineKeyboardBuilder()
        buttons = [InlineKeyboardButton(text=source_name, callback_data=f"loan_{source_id}")
                   for source_id, source_name in self.context.db.get_sources()]
        for but in buttons:
            builder.row(but)
        await message.answer(text="Выберите РЕАЛЬНЫЙ источник", reply_markup=builder.as_markup())


class ScheduleMessageFactory(MessageFactory):
    alias: str = 'schedule'
    async def callback(self, message: Message) -> None:
        text = ""
        prev_date = None
        all_total = 0
        day_total = 0
        for i, (loan_id, source_id, source_name, loan_date, expected_settle_date,
            amount, total, legend_id, legend_name, comment) in enumerate(self.context.db.get_unsettled_loans()):
            if prev_date != expected_settle_date:
                text += f"\t{prev_date}: {day_total} рублей\n"
                prev_date = expected_settle_date
                day_total = 0
            text += f"{i + 1}. {total} от {loan_date} ({legend_name}) -- '{comment}' ({source_name})\n"
            all_total += total
            day_total += total
        text += f"\t{prev_date}: {day_total} рублей\n"
        text += f"Итого: {all_total} рублей"
        await message.answer(text=text, reply_markup=self.get_kb())


class AnalyticsMessageFactory(MessageFactory):
    alias: str = 'analytics'
    async def callback(self, message: Message) -> None:
        await message.answer(text="Функционал ещё не поддержан", reply_markup=self.get_kb())
