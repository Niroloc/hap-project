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

    def get_kb(self) -> ReplyKeyboardMarkup:
        buttons = [KeyboardButton(text=k) for k in self.context.button_to_factory]
        buttons = [buttons[i: i + 2] for i in range(0, len(buttons), 2)]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=False)

    @abstractmethod
    def _parse_args(self, callback_data: str) -> None:
        pass

    @abstractmethod
    async def callback(self, callback: CallbackQuery) -> None:
        pass


class PaybackCallbackFactory(CallbackFactory):
    prefix: str = "payback"
    def __init__(self, context: Context):
        super().__init__(context)
        self.loan_id: int|None = None
        self.quantity: int|None = None
        self.payback_date: date|None = None
        self.deserializers: list[Callable[[str], Any]] = [
            lambda x: int(x),
            lambda x: int(x),
            lambda x: datetime.strptime(x, "%Y-%m-%d").date()
        ]
        self.args_count: int = 0

    def _parse_args(self, callback_data: str) -> None:
        self.args_count = 0
        args = callback_data.split('_')
        deserialized_args = [None] * len(self.deserializers)
        for i, (arg, deserializer) in enumerate(
                zip(
                    args[1: len(self.deserializers)],
                    self.deserializers[: len(args[1:])]
                )
        ):
            try:
                deserialized_args[i] = deserializer(arg)
                self.args_count = i + 1
            except Exception as err:
                logging.error(f"Error {err} while processing args for {self.__name__}")
                logging.error(format_exc())
                break
        self.loan_id, self.quantity, self.payback_date = deserialized_args

    async def callback(self, callback: CallbackQuery) -> None:
        self._parse_args(callback_data=callback.data)
        if self.args_count == 0:
            pass
        elif self.args_count == 1:
            pass
        elif self.args_count == 2:
            pass
        elif self.args_count == 3:
            pass
        else:
            logging.error(format_exc())
            await callback.answer()
            await callback.message.answer(text="Что-то с кнопкой не то...", reply_markup=self.get_kb())