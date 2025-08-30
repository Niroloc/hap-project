import logging
from abc import ABC, abstractmethod
from traceback import format_exc
from datetime import datetime, date

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.context.context import Context

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
        self.context.input_mode_callback_data += "_" + message.text
        builder.row(InlineKeyboardButton(text="Продолжить", callback_data=self.context.input_mode_callback_data))
        await message.answer(text="Продолжить?", reply_markup=builder.as_markup())
        self.context.input_mode_callback_data = None

class CommentMessageFactory(MessageFactory):
    alias: str = 'comment'
    def __init__(self, context: Context):
        super().__init__(context)
        self.mod = 3
        self.loan_id: int | None = None
        self.comment: str | None = None

    async def callback(self, message: Message) -> None:
        if self.step == 0:
            text = ""
            buttons = []
            for (loan_id, source_id, source_name, loan_date, expected_settle_date,
                 amount, total, legend_id, legend_name, comment) in self.context.db.get_unsettled_loans():
                text += (f"{loan_id}. {legend_name}({source_name}) -- {amount} -> {total} -- "
                         f"{datetime.strptime(loan_date, '%Y-%m-%d').strftime('%d.%m.%Y')} -> "
                         f"{datetime.strptime(expected_settle_date, '%Y-%m-%d').strftime('%d.%m.%Y')}\n")
                buttons.append(KeyboardButton(text=str(loan_id)))
            special_keyboard = ReplyKeyboardMarkup(
                keyboard=[buttons[i: i+3] for i in range(0, len(buttons), 3)],
                resize_keyboard=True
            )
            await message.answer(
                text="Введите номер займа для добавления комментария:\n"+text,
                reply_markup=special_keyboard
            )
            self.context.input_mode_message_alias = self.alias
        elif self.step == 1:
            try:
                self.loan_id = int(message.text)
            except:
                logging.error("Error while parsing loan_id for adding comment")
                logging.error(format_exc())
                return
            await message.answer(text="Введите комментарий к займу", reply_markup=self.get_kb())
        elif self.step == 2:
            self.comment = message.text
            if self.context.db.update_loan_comment(self.loan_id, self.comment):
                await message.answer(text="Отлично! Комментарий добавлен", reply_markup=self.get_kb())
            else:
                await message.answer(text="Какая-то ошибка", reply_markup=self.get_kb())
        self.step = (self.step + 1) % self.mod


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
            text=f"{total} ({legend_name}) до "
                 f"{datetime.strptime(expected_settle_date, '%Y-%m-%d').strftime('%d.%m.%Y')}",
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
        prev_date: date | None = None
        all_total = 0
        day_total = 0
        for i, (loan_id, source_id, source_name, loan_date, expected_settle_date,
            amount, total, legend_id, legend_name, comment) in enumerate(self.context.db.get_unsettled_loans()):
            expected_settle_date = datetime.strptime(expected_settle_date, '%Y-%m-%d')
            if prev_date != expected_settle_date:
                if prev_date is not None:
                    text += f"\n{prev_date.strftime('%d.%m')}: {day_total} рублей\n\n"
                prev_date = expected_settle_date
                day_total = 0
            text += (f"{i + 1}. {total} по займу от {datetime.strptime(loan_date, '%Y-%m-%d').strftime('%d.%m')} "
                     f"({legend_name}) -- '{comment if comment is not None else str()}' ({source_name})\n")
            all_total += total
            day_total += total
        if prev_date is not None:
            text += f"\n{prev_date.strftime('%d.%m')}: {day_total} рублей\n\n"
        text += f"Итого: {all_total} рублей"
        await message.answer(text=text, reply_markup=self.get_kb())


class AnalyticsMessageFactory(MessageFactory):
    alias: str = 'analytics'
    async def callback(self, message: Message) -> None:
        await message.answer(text="Функционал ещё не поддержан", reply_markup=self.get_kb())
