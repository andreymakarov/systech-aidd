import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from src.bot.config import Config
from src.bot.handlers import MessageHandler


class TelegramBot:
    """Telegram бот с polling"""

    def __init__(self, config: Config, message_handler: MessageHandler):
        self.config = config
        self.message_handler = message_handler
        self.bot = Bot(
            token=config.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()
        self._register_handlers()

    def _register_handlers(self):
        """Регистрация обработчиков сообщений"""
        self.dp.message.register(
            self.message_handler.handle_start_command,
            lambda message: message.text == "/start"
        )

    async def start(self):
        """Запуск бота"""
        logging.info("Бот запущен")
        await self.dp.start_polling(self.bot)

    async def stop(self):
        """Остановка бота"""
        logging.info("Бот остановлен")
        await self.bot.session.close()

