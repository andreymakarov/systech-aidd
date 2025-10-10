import asyncio
import logging
from src.bot.config import Config
from src.bot.handlers import MessageHandler
from src.bot.bot import TelegramBot


def setup_logging():
    """Настройка базового логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


async def main():
    """Главная функция приложения"""
    setup_logging()

    try:
        # Инициализация компонентов
        config = Config()
        message_handler = MessageHandler()
        bot = TelegramBot(config, message_handler)

        # Запуск бота
        await bot.start()
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        return
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Получен сигнал остановки")

