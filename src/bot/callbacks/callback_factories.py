import logging
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from traceback import format_exc
from typing import Callable, Any

from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, FSInputFile, \
    InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder

from src.context.context import Context


class CallbackFactory(ABC):
    prefix: str = "unknown"
    def __init__(self, context: Context):
        self.context = context
        self.deserializers: list[Callable[[str], Any]] = []
        self.args_count: int = 0

    def get_kb(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=k) for k in self.context.BUTTON_TO_ALIAS]
        buttons = [buttons[i: i + 2] for i in range(0, len(buttons), 2)]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)

    def _preproc(self, callback_data: str) -> list:
        self.args_count = 0
        args = callback_data.split('_')[1: ]
        deserialized_args = [None] * len(self.deserializers)
        length = min(len(args), len(self.deserializers))
        for i, (arg, deserializer) in enumerate(
                zip(
                    args[: length],
                    self.deserializers[: length]
                )
        ):
            try:
                deserialized_args[i] = deserializer(arg)
                self.args_count += 1
            except Exception as err:
                logging.warning(f"Error {err} while processing args for {self.__class__.__name__} from {callback_data}")
                logging.warning(format_exc())
                break
        return deserialized_args

    @abstractmethod
    def _parse_args(self, callback_data: str) -> None:
        pass

    @abstractmethod
    async def callback(self, callback: CallbackQuery) -> None:
        pass


class LoanCallbackFactory(CallbackFactory):
    prefix: str = "loan"
    def __init__(self, context):
        super().__init__(context)
        self.source_id: int | None = None
        self.legend_id: int | None = None
        self.loan_date: date | None = None
        self.expected_settle_date: date | None = None
        self.amount: int | None = None
        self.reward: int | None = None

        self.deserializers: list[Callable[[str], Any]] = [
            lambda x: int(x),
            lambda x: int(x),
            lambda x: datetime.strptime(x, "%Y-%m-%d").date(),
            lambda x: datetime.strptime(x, "%Y-%m-%d").date(),
            lambda x: int(x),
            lambda x: int(x)
        ]

    def _parse_args(self, callback_data: str) -> None:
        (self.source_id, self.legend_id, self.loan_date, self.expected_settle_date,
         self.amount, self.reward) = self._preproc(callback_data)

    async def callback(self, callback: CallbackQuery) -> None:
        self._parse_args(callback_data=callback.data)
        if self.args_count == 1:
            self.context.input_mode_callback_data = None
            builder = InlineKeyboardBuilder()
            buttons = [
                InlineKeyboardButton(text=legend_name, callback_data=callback.data+f"_{legend_id}")
                for legend_id, legend_name in self.context.db.get_legend_sources()
            ]
            for but in buttons:
                builder.row(but)
            await callback.message.edit_text(text="А теперь выберите легенду", reply_markup=builder.as_markup())
        elif self.args_count == 2:
            self.context.input_mode_callback_data = None
            builder = InlineKeyboardBuilder()
            buttons = [
                InlineKeyboardButton(text=dt.strftime("%d.%m.%Y"),
                                     callback_data=callback.data + f"_{dt.strftime('%Y-%m-%d')}")
                for dt in [date.today() + timedelta(days=i) for i in range(-7, 7)]
            ]
            builder.row(*buttons[: 7])
            builder.row(buttons[7])
            builder.row(*buttons[8:])
            await callback.message.edit_text(text="Выберите дату выдачи займа", reply_markup=builder.as_markup())
        elif self.args_count == 3:
            self.context.input_mode_callback_data = None
            builder = InlineKeyboardBuilder()
            month = date.today().month
            year = date.today().year
            last_day_of_month = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            buttons = []
            for _ in range(4):
                dt = date(year=year, month=month, day=15)
                buttons.append(
                    InlineKeyboardButton(
                        text=dt.strftime("%d.%m.%Y"),
                        callback_data=callback.data+f"_{dt.strftime('%Y-%m-%d')}"
                    )
                )
                dt = date(year=year, month=month, day=last_day_of_month[month])
                buttons.append(
                    InlineKeyboardButton(
                        text=dt.strftime("%d.%m.%Y"),
                        callback_data=callback.data+f"_{dt.strftime('%Y-%m-%d')}"
                    )
                )
                year += month // 12
                month = month % 12 + 1
            for i in range(0, len(buttons), 2):
                builder.row(*buttons[i: i + 2])
            await callback.message.edit_text(text="Укажите ожидаемую дату возврата займа", reply_markup=builder.as_markup())
        elif self.args_count == 4:
            self.context.input_mode_callback_data = None
            builder = InlineKeyboardBuilder()
            buttons = [
                InlineKeyboardButton(text=str(i), callback_data=callback.data + f"_{i}")
                for i in range(5000, 30001, 5000)
            ]
            for i in range(0, len(buttons), 2):
                builder.row(*buttons[i: i + 2])
            self.context.input_mode_callback_data = callback.data
            await callback.message.edit_text(text="Выберите или введите сумму займа", reply_markup=builder.as_markup())
        elif self.args_count == 5:
            self.context.input_mode_callback_data = None
            builder = InlineKeyboardBuilder()
            buttons = [
                InlineKeyboardButton(text=str(i), callback_data=callback.data+f"_{i}")
                for i in range(5000, 30001, 5000)
            ]
            for i in range(0, len(buttons), 2):
                builder.row(*buttons[i: i + 2])
            self.context.input_mode_callback_data = callback.data
            await callback.message.edit_text(
                text="Укажите или введите сумму процентов в рублях",
                reply_markup=builder.as_markup()
            )
        elif self.args_count == 6:
            self.context.input_mode_callback_data = None
            if self.context.db.create_loan(
                    self.source_id,
                    self.loan_date,
                    self.amount,
                    self.reward,
                    self.expected_settle_date,
                    self.legend_id
            ):
                await callback.message.answer(
                    text=f"Займ от {self.context.db.get_legend_source_name_by_id(self.legend_id)}"
                         f"({self.context.db.get_source_name_by_id(self.source_id)}) "
                         f"на сумму {self.amount}, "
                         f"к возврату {self.amount + self.reward} {self.expected_settle_date.strftime('%d.%m.%Y')} "
                         f"успешно оформлен!",
                    reply_markup=self.get_kb()
                )
            else:
                await callback.message.answer(
                    text="Ошибка, проверяем логи!",
                    reply_markup=self.get_kb()
                )
        else:
            logging.error(f"An error occurred while processing callback for {callback.data} in {self.__class__.__name__}")
            await callback.message.answer(text="Ой ёй..")
        await callback.answer()

class PaybackCallbackFactory(CallbackFactory):
    prefix: str = "payback"
    def __init__(self, context: Context):
        super().__init__(context)
        self.loan_id: int | None = None
        self.settle_date: date | None = None
        self.amount: int | None = None
        self.new_reward: int | None = None
        self.new_expected_settle_date: date | None = None
        self.deserializers: list[Callable[[str], Any]] = [
            lambda x: int(x),
            lambda x: datetime.strptime(x, "%Y-%m-%d").date(),
            lambda x: int(x),
            lambda x: int(x),
            lambda x: datetime.strptime(x, "%Y-%m-%d").date()
        ]

    def _parse_args(self, callback_data: str) -> None:
        (self.loan_id, self.settle_date, self.amount,
         self.new_reward, self.new_expected_settle_date) = self._preproc(callback_data)

    async def callback(self, callback: CallbackQuery) -> None:
        self._parse_args(callback_data=callback.data)
        if self.args_count == 1:
            self.context.input_mode_callback_data = None
            builder = InlineKeyboardBuilder()
            buttons = [
                InlineKeyboardButton(text=dt.strftime("%d.%m.%Y"),
                                     callback_data=callback.data+f"_{dt.strftime('%Y-%m-%d')}")
                for dt in [date.today() + timedelta(days=i) for i in range(-7, 7)]
            ]
            builder.row(*buttons[: 7])
            builder.row(buttons[7])
            builder.row(*buttons[8: ])
            await callback.message.edit_text(text="Выберите дату погашения задолженности",
                                             reply_markup=builder.as_markup())
        elif self.args_count == 2:
            self.context.input_mode_callback_data = None
            amount = self.context.db.get_loan_amount(self.loan_id)
            builder = InlineKeyboardBuilder()
            buttons = [
                InlineKeyboardButton(text=str(i), callback_data=callback.data + f"_{i}")
                for i in range(5000, 30001, 5000)
            ]
            builder.row(InlineKeyboardButton(text="Полное погашение", callback_data=callback.data+f"_{amount}"))
            for i in range(0, len(buttons), 2):
                builder.row(*buttons[i: i + 2])
            self.context.input_mode_callback_data = callback.data
            await callback.message.answer(text="Выберите или введите сумму погашения", reply_markup=builder.as_markup())
        elif self.args_count == 3:
            self.context.input_mode_callback_data = None
            if self.amount >= self.context.db.get_loan_amount(self.loan_id):
                if self.context.db.settle_loan(self.loan_id, self.settle_date):
                    await callback.message.answer(text="Кажется, займ можно закрывать, уже готово",
                                                  reply_markup=self.get_kb())
                else:
                    await callback.message.answer(text="Займ можно было бы закрыть, но что-то пошло не так",
                                                  reply_markup=self.get_kb())
            else:
                builder = InlineKeyboardBuilder()
                buttons = [
                    InlineKeyboardButton(text=str(i), callback_data=callback.data+f"_{i}")
                    for i in range(5000, 30001, 5000)
                ]
                for i in range(0, len(buttons), 2):
                    builder.row(*buttons[i: i + 2])
                self.context.input_mode_callback_data = callback.data
                await callback.message.edit_text(text="Выберите или введите сумму процентов за продление в рублях",
                                              reply_markup=builder.as_markup())
        elif self.args_count == 4:
            self.context.input_mode_callback_data = None
            builder = InlineKeyboardBuilder()
            month = date.today().month
            year = date.today().year
            last_day_of_month = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            buttons = []
            for _ in range(4):
                dt = date(year=year, month=month, day=15)
                buttons.append(
                    InlineKeyboardButton(
                        text=dt.strftime("%d.%m.%Y"),
                        callback_data=callback.data + f"_{dt.strftime('%Y-%m-%d')}"
                    )
                )
                dt = date(year=year, month=month, day=last_day_of_month[month])
                buttons.append(
                    InlineKeyboardButton(
                        text=dt.strftime("%d.%m.%Y"),
                        callback_data=callback.data + f"_{dt.strftime('%Y-%m-%d')}"
                    )
                )
                year += month // 12
                month = month % 12 + 1
            for i in range(0, len(buttons), 2):
                builder.row(*buttons[i: i + 2])
            await callback.message.edit_text(text="Выберите дату ожидаемого погашения продления",
                                          reply_markup=builder.as_markup())
        elif self.args_count == 5:
            self.context.input_mode_callback_data = None
            if self.context.db.settle_loan(self.loan_id, self.settle_date, self.amount,
                                        self.new_reward, self.new_expected_settle_date):
                await callback.message.answer(text=f"Продление займа №{self.loan_id} до "
                                                   f"{self.new_expected_settle_date.strftime('%d.%m.%Y')} "
                                                   f"успешно выполнено",
                                              reply_markup=self.get_kb())
            else:
                await callback.message.answer(text="Ох ты ж ё...", reply_markup=self.get_kb())

        else:
            logging.error(f"An error occurred while processing callback for {callback.data} in {self.__class__.__name__}")
            await callback.message.answer(text="Что-то не то...", reply_markup=self.get_kb())
        await callback.answer()


class AnalyticsCallbackFactory(CallbackFactory):
    prefix: str = 'analytics'
    def __init__(self, context: Context):
        super().__init__(context)
        self.by: str | None = None
        self.year: int | None = None
        self.month: int | None = None
        self.deserializers: list[Callable[[str], Any]] = [
            lambda x: x,
            lambda x: int(x),
            lambda x: int(x)
        ]
        self.by_to_callback = {
            "source": lambda *x: self.context.reporter.get_graphic_by_sources('source_name', *x),
            "legend": lambda *x: self.context.reporter.get_graphic_by_sources('legend_name', *x)
        }

    def _parse_args(self, callback_data: str) -> None:
        self.by, self.year, self.month = self._preproc(callback_data)

    async def callback(self, callback: CallbackQuery) -> None:
        self._parse_args(callback.data)
        if self.args_count == 1:
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="Все время наблюдений", callback_data=callback.data+"_-1"))
            buttons = [
                InlineKeyboardButton(
                    text=str(i),
                    callback_data=callback.data+f"_{i}"
                )
                for i in range(date.today().year - 4, date.today().year + 1)
            ]
            builder.row(*buttons)
            await callback.message.edit_text(text="Выберите год для аналитики", reply_markup=builder.as_markup())
        elif self.args_count == 2:
            if self.year == -1:
                graphics = self.by_to_callback[self.by]()
                await callback.message.answer(text="Ожидайте фото следующим сообщением", reply_markup=self.get_kb())
                await callback.message.answer_media_group(media=self._get_group_for_sending_graphics(graphics))
            else:
                builder = InlineKeyboardBuilder()
                builder.row(InlineKeyboardButton(text="Весь год", callback_data=callback.data + "_-1"))
                buttons = [
                    InlineKeyboardButton(
                        text=str(i),
                        callback_data=callback.data + f"_{i}"
                    )
                    for i in range(1, 13)
                ]
                builder.row(*buttons)
                await callback.message.edit_text(text="Выберите месяц для аналитики", reply_markup=builder.as_markup())
        elif self.args_count == 4:
            if self.month == -1:
                self.month = None
            graphics = self.by_to_callback[self.by](self.year, self.month)
            await callback.message.answer(text="Ожидайте фото следующим сообщением", reply_markup=self.get_kb())
            await callback.message.answer_media_group(media=self._get_group_for_sending_graphics(graphics))
        await callback.answer()

    def _get_group_for_sending_graphics(self, graphics: list[str]) -> list[InputMediaPhoto]:
        builder = MediaGroupBuilder(caption="Графики подъехали")
        for g in graphics:
            builder.add(type="photo", media=FSInputFile(g))
        return builder.build()
