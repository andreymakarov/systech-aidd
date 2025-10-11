import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import Config
from bot.handlers import MessageHandler


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
        self.dp.message.register(
            self.message_handler.handle_start_command,
            lambda message: message.text == "/start",
        )

        # Команда /clear
        self.dp.message.register(
            self.message_handler.handle_clear_command,
            lambda message: message.text == "/clear",
        )

        # Текстовые сообщения (не команды)
        self.dp.message.register(
            self.message_handler.handle_text_message,
            lambda message: message.text and not message.text.startswith("/"),
        )

        # Нетекстовые сообщения (фото, файлы, стикеры и т.д.)
        self.dp.message.register(
            self.message_handler.handle_non_text_message,
            lambda message: not message.text,
        )

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
