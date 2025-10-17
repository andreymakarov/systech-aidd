import asyncio
import contextlib
import logging
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from bot.bot import TelegramBot
from bot.config import Config
from bot.conversation import ConversationManager
from bot.handlers import MessageHandler
from bot.llm_client import LLMClient
from bot.role_manager import RoleManager


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
        # Готовим async engine/session factory (DI для ConversationManager)
        os.makedirs(os.path.dirname(config.db_path), exist_ok=True)
        database_url = f"sqlite+aiosqlite:///{config.db_path}"
        engine: AsyncEngine = create_async_engine(database_url, future=True)
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        conversation_manager = ConversationManager(session_factory)
        llm_client = LLMClient(config)
        role_manager = RoleManager(config.role_prompt_file)
        message_handler = MessageHandler(llm_client, conversation_manager, role_manager)
        bot = TelegramBot(config, message_handler)

        # Запуск бота
        logging.info("Запуск бота...")
        await bot.start()
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        return
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Тихий выход при Ctrl+C - основная обработка уже в bot.stop()
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
