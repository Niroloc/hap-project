import logging
from abc import ABC, abstractmethod
from datetime import date, datetime
from traceback import format_exc
from typing import Callable, Any, Coroutine

from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, KeyboardButton

from src.context.context import Context


class CallbackFactory(ABC):
    prefix: str = "unknown"
    def __init__(self, context: Context):
        self.context = context
        self.deserializers: list[Callable[[str], Any]] = []
        self.args_count: int = 0

    def get_kb(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=k) for k in self.context.BUTTON_TO_FACTORY]
        buttons = [buttons[i: i + 2] for i in range(0, len(buttons), 2)]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)

    def _preproc(self, callback_data: str) -> list:
        self.args_count = 0
        args = callback_data.split('_')
        deserialized_args = [None] * len(self.deserializers)
        for i, (arg, deserializer) in enumerate(
                zip(
                    args[1: len(self.deserializers)],
                    self.deserializers[: len(args) - 1]
                )
        ):
            try:
                deserialized_args[i] = deserializer(arg)
                self.args_count += 1
            except Exception as err:
                logging.error(f"Error {err} while processing args for {self.__name__} from {callback_data}")
                logging.error(format_exc())
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
        self.expected_settle_date: date | None = None
        self.amount: int | None = None
        self.reward: int | None = None
        self.comment: str | None = None
        self.deserializers: list[Callable[[str], Any]] = [
            lambda x: int(x),
            lambda x: int(x),
            lambda x: datetime.strptime(x, "%Y-%m-%d").date(),
            lambda x: int(x),
            lambda x: int(x),
            lambda x: x
        ]

    def _parse_args(self, callback_data: str) -> None:
        (self.source_id, self.legend_id, self.expected_settle_date,
         self.amount, self.reward, self.comment) = self._preproc(callback_data)

    async def callback(self, callback: CallbackQuery) -> None:
        self._parse_args(callback_data=callback.data)
        if self.args_count == 1:
            pass
        elif self.args_count == 2:
            pass
        elif self.args_count == 3:
            pass
        elif self.args_count == 4:
            pass
        elif self.args_count == 5:
            pass
        elif self.args_count == 6:
            pass
        else:
            logging.error(f"An error occurred while processing callback for {callback.data} in {self.__name__}")
            await callback.message.answer(text="Ой ёй..")
        await callback.answer()

class PaybackCallbackFactory(CallbackFactory):
    prefix: str = "payback"
    def __init__(self, context: Context):
        super().__init__(context)
        self.loan_id: int | None = None
        self.amount: int | None = None
        self.settle_date: date | None = None
        self.new_reward: int | None = None
        self.new_expected_settle_date: date | None = None
        self.deserializers: list[Callable[[str], Any]] = [
            lambda x: int(x),
            lambda x: int(x),
            lambda x: datetime.strptime(x, "%Y-%m-%d").date(),
            lambda x: int(x),
            lambda x: datetime.strptime(x, "%Y-%m-%d").date()
        ]

    def _parse_args(self, callback_data: str) -> None:
        deserialized_args = self._preproc(callback_data)
        self.loan_id, self.amount, self.settle_date, self.new_reward, self.new_expected_settle_date = deserialized_args

    async def callback(self, callback: CallbackQuery) -> None:
        self._parse_args(callback_data=callback.data)
        if self.args_count == 1:
            pass
        elif self.args_count == 2:
            pass
        elif self.args_count == 3:
            pass
        else:
            logging.error(f"An error occurred while processing callback for {callback.data} in {self.__name__}")
            await callback.message.answer(text="Что-то не то...", reply_markup=self.get_kb())
        await callback.answer()