import logging
from aiogram.types import Message
from aiogram.enums import ChatAction
from src.bot.llm_client import LLMClient


class MessageHandler:
    """Обработчик сообщений от пользователей"""

    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client

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

    async def handle_text_message(self, message: Message):
        """Обработчик текстовых сообщений"""
        user_id = message.from_user.id
        text = message.text
        logging.info(f"User {user_id} sent message ({len(text)} chars)")

        try:
            # Показываем "печатает..."
            await message.bot.send_chat_action(
                chat_id=message.chat.id,
                action=ChatAction.TYPING
            )

            # Получаем ответ от LLM
            response = await self.llm_client.generate_response(text)

            # Отправляем ответ пользователю
            await message.answer(response)
            logging.info(f"Response sent to user {user_id}")

        except Exception as e:
            logging.error(f"Error processing message from user {user_id}: {e}")
            await message.answer(
                "Произошла ошибка при обработке запроса. Попробуйте позже."
            )

