from typing import Callable, Any, Coroutine

from aiogram.types import Message

from src.bot.callbacks.callback_factories import CallbackFactory
from src.bot.callbacks.message_factories import MessageFactory
from src.context.context import Context
from src.bot.callbacks.callback_factories import *
from src.bot.callbacks.message_factories import *


class CallbackHelper:
    def __init__(self, context: Context):
        self.context = context
        self.prefix_to_callback_factory: dict[str, CallbackFactory] = {
            cls.prefix: cls(context) for cls in CallbackFactory.__subclasses__()
        }
        self.alias_to_factory: dict[str, MessageFactory] = {
            cls.alias: cls(context) for cls in MessageFactory.__subclasses__()
        }
        self.default_message_factory: MessageFactory = self.alias_to_factory.get(
            context.DEFAULT_MESSAGE_FACTORY_ALIAS,
            ScheduleMessageFactory
        )

    def get_message_callback(self, text: str) -> Callable[[Message], Coroutine[Any, Any, None]]:
        if text not in self.context.BUTTON_TO_ALIAS:
            if self.context.input_mode_callback_data is not None:
                self.context.input_mode_message_alias = None
                return InputMessageFactory(self.context).callback
            elif self.context.input_mode_message_alias is not None:
                self.context.input_mode_callback_data = None
                return self.alias_to_factory[self.context.input_mode_message_alias].callback
            return self.default_message_factory.callback

        self.context.input_mode_message_alias = None
        self.context.input_mode_callback_data = None

        alias = self.context.BUTTON_TO_ALIAS[text]

        if alias != 'analytics':
            self.context.rebuild_reporter_movements = True
        elif self.context.rebuild_reporter_movements:
            self.context.reporter.get_movements()
            self.context.rebuild_reporter_movements = False

        if alias not in self.alias_to_factory:
            logging.warning(f"Cannot find factory for alias '{alias}'")
            return self.default_message_factory.callback
        self.alias_to_factory[self.context.BUTTON_TO_ALIAS[text]].step = 0
        return self.alias_to_factory[self.context.BUTTON_TO_ALIAS[text]].callback

    def get_callback_factory(self, callback_data: str) -> CallbackFactory | None:
        prefix = callback_data.split("_")[0]
        if prefix not in self.prefix_to_callback_factory:
            logging.error(f"Prefix {callback_data} is not valid")
            return None
        return self.prefix_to_callback_factory[prefix]
