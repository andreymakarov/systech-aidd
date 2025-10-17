"""Telegram bot implementation with aiogram."""

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

from bot.config import Config
from bot.handlers import MessageHandler


# Фильтры для сообщений
def is_start_command(message: Message) -> bool:
    """Проверка команды /start"""
    return message.text == "/start"


def is_clear_command(message: Message) -> bool:
    """Проверка команды /clear"""
    return message.text == "/clear"


def is_role_command(message: Message) -> bool:
    """Проверка команды /role"""
    return message.text == "/role"


def is_regular_text(message: Message) -> bool:
    """Проверка обычного текстового сообщения (не команда)"""
    return bool(message.text and not message.text.startswith("/"))


def is_non_text(message: Message) -> bool:
    """Проверка нетекстового сообщения"""
    return not message.text


class TelegramBot:
    """Telegram бот с polling"""

    def __init__(self, config: Config, message_handler: MessageHandler) -> None:
        self.config = config
        self.message_handler = message_handler
        self.bot = Bot(
            token=config.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self.dp = Dispatcher()
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Регистрация обработчиков сообщений"""
        # Команда /start
        self.dp.message.register(self.message_handler.handle_start_command, is_start_command)

        # Команда /role
        self.dp.message.register(self.message_handler.handle_role_command, is_role_command)

        # Команда /clear
        self.dp.message.register(self.message_handler.handle_clear_command, is_clear_command)

        # Текстовые сообщения (не команды)
        self.dp.message.register(self.message_handler.handle_text_message, is_regular_text)

        # Нетекстовые сообщения (фото, файлы, стикеры и т.д.)
        self.dp.message.register(self.message_handler.handle_non_text_message, is_non_text)

    async def start(self) -> None:
        """Запуск бота"""
        logging.info("Бот запущен")
        try:
            await self.dp.start_polling(self.bot)
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Остановка бота"""
        logging.info("Останавливаем бота...")
        await self.bot.session.close()
        logging.info("Бот остановлен")

