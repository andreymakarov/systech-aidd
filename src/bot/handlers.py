import logging

from aiogram.enums import ChatAction
from aiogram.types import Message

from bot.conversation import ConversationManager
from bot.llm_client import LLMClient


class MessageHandler:
    """Обработчик сообщений от пользователей"""

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        conversation_manager: ConversationManager | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.conversation_manager = conversation_manager

    async def handle_start_command(self, message: Message) -> None:
        """Обработчик команды /start"""
        user_id = message.from_user.id  # type: ignore[union-attr]
        logging.info(f"User {user_id} executed /start command")

        welcome_text = (
            "Привет! Я AI-ассистент. Задай мне любой вопрос!\n\n"
            "Доступные команды:\n"
            "/start - приветствие\n"
            "/clear - очистить историю диалога"
        )

        await message.answer(welcome_text)

    async def handle_text_message(self, message: Message) -> None:
        """Обработчик текстовых сообщений"""
        user_id = message.from_user.id  # type: ignore[union-attr]
        text = message.text
        if text is None:
            return

        logging.info(f"User {user_id} sent message ({len(text)} chars)")

        try:
            # Показываем "печатает..."
            if message.bot:
                await message.bot.send_chat_action(
                    chat_id=message.chat.id, action=ChatAction.TYPING
                )

            # Получаем историю диалога
            assert self.conversation_manager is not None
            history = self.conversation_manager.get_history(user_id)

            # Формируем запрос: system prompt + история + новое сообщение
            assert self.llm_client is not None
            messages = [
                {"role": "system", "content": self.llm_client.config.system_prompt},
                *history,
                {"role": "user", "content": text},
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
            await message.answer("Произошла ошибка при обработке запроса. Попробуйте позже.")

    async def handle_clear_command(self, message: Message) -> None:
        """Обработчик команды /clear"""
        user_id = message.from_user.id  # type: ignore[union-attr]
        logging.info(f"User {user_id} executed /clear command")

        # Очищаем историю диалога
        assert self.conversation_manager is not None
        self.conversation_manager.clear_history(user_id)

        await message.answer("История диалога очищена")

    async def handle_non_text_message(self, message: Message) -> None:
        """Обработчик нетекстовых сообщений"""
        user_id = message.from_user.id  # type: ignore[union-attr]
        logging.info(f"User {user_id} sent non-text message")

        await message.answer("Я работаю только с текстовыми сообщениями")
