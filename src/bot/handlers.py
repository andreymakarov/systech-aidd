import logging
from aiogram.types import Message
from aiogram.enums import ChatAction
from src.bot.llm_client import LLMClient
from src.bot.conversation import ConversationManager


class MessageHandler:
    """Обработчик сообщений от пользователей"""

    def __init__(self, llm_client: LLMClient = None, conversation_manager: ConversationManager = None):
        self.llm_client = llm_client
        self.conversation_manager = conversation_manager

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

            # Получаем историю диалога
            history = self.conversation_manager.get_history(user_id)

            # Формируем запрос: system prompt + история + новое сообщение
            messages = [
                {"role": "system", "content": self.llm_client.config.system_prompt},
                *history,
                {"role": "user", "content": text}
            ]

            # Получаем ответ от LLM
            response = await self.llm_client.generate_response(messages)

            # Сохраняем сообщение пользователя и ответ в историю
            self.conversation_manager.add_message(user_id, "user", text)
            self.conversation_manager.add_message(user_id, "assistant", response)

            # Отправляем ответ пользователю
            await message.answer(response)
            logging.info(f"Response sent to user {user_id}")

        except Exception as e:
            logging.error(f"Error processing message from user {user_id}: {e}")
            await message.answer(
                "Произошла ошибка при обработке запроса. Попробуйте позже."
            )

