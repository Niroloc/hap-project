from src.context.context import Context
from src.bot.callbacks.callback_factories import *
from src.bot.callbacks.message_factories import *


class FactoryHelper:
    def __init__(self, context: Context):
        self.context = context
        self.prefix_to_callback_factory: dict[str, CallbackFactory] = {
            cls.prefix: cls(context) for cls in CallbackFactory.__subclasses__()
        }
        self.alias_to_factory: dict[str, MessageFactory] = {
            cls.message: cls(context) for cls in MessageFactory.__subclasses__()
        }
        self.default_message_factory: MessageFactory = self.alias_to_factory.get(
            context.DEFAULT_MESSAGE_FACTORY_ALIAS,
            PaybackMessageFactory
        )

    def get_message_factory(self, text: str) -> MessageFactory:
        if text not in self.context.button_to_factory:
            return self.default_message_factory
        alias = self.context.button_to_factory[text]
        logging.warning(f"Cannot find factory for alias '{alias}'")
        if alias not in self.alias_to_factory:
            return self.default_message_factory
        return self.alias_to_factory[self.context.button_to_factory[text]]

    def get_callback_factory(self, callback_data: str) -> CallbackFactory | None:
        prefix = callback_data.split("_")[0]
        if prefix not in self.prefix_to_callback_factory:
            logging.error(f"Alias {callback_data} is not valid")
            return None
        return self.prefix_to_callback_factory[prefix]
