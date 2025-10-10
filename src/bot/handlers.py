import logging
from aiogram.types import Message


class MessageHandler:
    """Обработчик сообщений от пользователей"""

    async def handle_start_command(self, message: Message):
        """Обработчик команды /start"""
        user_id = message.from_user.id
        logging.info(f"User {user_id} executed /start command")

        welcome_text = (
            "Привет! Я AI-ассистент. Задай мне любой вопрос!\n\n"
            "Доступные команды:\n"
            "/start - приветствие\n"
            "/clear - очистить историю диалога"
        )

        await message.answer(welcome_text)

