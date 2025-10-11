import asyncio
import logging

from dotenv import load_dotenv

from bot.bot import TelegramBot
from bot.config import Config
from bot.conversation import ConversationManager
from bot.handlers import MessageHandler
from bot.llm_client import LLMClient


def setup_logging() -> None:
    """Настройка базового логирования"""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


async def main() -> None:
    """Главная функция приложения"""
    load_dotenv()
    setup_logging()

    try:
        # Инициализация компонентов
        logging.info("Инициализация компонентов...")
        config = Config()
        conversation_manager = ConversationManager()
        llm_client = LLMClient(config)
        message_handler = MessageHandler(llm_client, conversation_manager)
        bot = TelegramBot(config, message_handler)

        # Запуск бота
        logging.info("Запуск бота...")
        await bot.start()
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        return
    except KeyboardInterrupt:
        logging.info("Получен сигнал остановки (Ctrl+C)")
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
