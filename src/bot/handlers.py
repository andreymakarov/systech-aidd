import logging

from aiogram.enums import ChatAction
from aiogram.types import Message

from bot.conversation import ConversationManager
from bot.llm_client import LLMClient
from bot.role_manager import RoleManager

# Константы сообщений
WELCOME_TEXT = """Привет! Я AI-ассистент. Задай мне любой вопрос!

Доступные команды:
/start - приветствие
/role - показать мою роль
/clear - очистить историю диалога"""

ERROR_MESSAGE = "Произошла ошибка при обработке запроса. Попробуйте позже."
NON_TEXT_MESSAGE = "Я работаю только с текстовыми сообщениями"
HISTORY_CLEARED_MESSAGE = "История диалога очищена"
ROLE_ERROR_MESSAGE = "Не удалось загрузить описание роли"


class MessageHandler:
    """Обработчик сообщений от пользователей"""

    def __init__(
        self,
        llm_client: LLMClient,
        conversation_manager: ConversationManager,
        role_manager: RoleManager | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.conversation_manager = conversation_manager
        self.role_manager = role_manager

    async def handle_start_command(self, message: Message) -> None:
        """Обработчик команды /start"""
        user_id = message.from_user.id  # type: ignore[union-attr]
        logging.info(f"User {user_id} executed /start command")
        await message.answer(WELCOME_TEXT)

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
            history = await self.conversation_manager.get_history(user_id)

            # Определяем системный промпт: RoleManager или fallback на Config
            system_prompt = (
                self.role_manager.load_role()
                if self.role_manager
                else self.llm_client.config.system_prompt
            )

            # Формируем запрос: system prompt + история (role/content) + новое сообщение
            # Явно указываем тип для совместимости с mypy
            history_llm: list[dict[str, str]] = [
                {"role": str(m["role"]), "content": str(m["content"])} for m in history
            ]
            base_messages: list[dict[str, str]] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ]
            # Встраиваем историю между system и текущим сообщением
            messages: list[dict[str, str]] = [base_messages[0], *history_llm, base_messages[1]]

            # Получаем ответ от LLM
            response = await self.llm_client.generate_response(messages)

            # Сохраняем сообщение пользователя и ответ в историю
            await self.conversation_manager.add_message(user_id, "user", text)
            await self.conversation_manager.add_message(user_id, "assistant", response)

            # Отправляем ответ пользователю
            await message.answer(response)
            logging.info(f"Response sent to user {user_id}")

        except Exception as e:
            logging.error(f"Error processing message from user {user_id}: {e}")
            await message.answer(ERROR_MESSAGE)

    async def handle_clear_command(self, message: Message) -> None:
        """Обработчик команды /clear"""
        user_id = message.from_user.id  # type: ignore[union-attr]
        logging.info(f"User {user_id} executed /clear command")

        # Очищаем историю диалога
        await self.conversation_manager.clear_history(user_id)

        await message.answer(HISTORY_CLEARED_MESSAGE)

    async def handle_non_text_message(self, message: Message) -> None:
        """Обработчик нетекстовых сообщений"""
        user_id = message.from_user.id  # type: ignore[union-attr]
        logging.info(f"User {user_id} sent non-text message")

        await message.answer(NON_TEXT_MESSAGE)

    async def handle_role_command(self, message: Message) -> None:
        """Обработчик команды /role"""
        user_id = message.from_user.id  # type: ignore[union-attr]
        logging.info(f"User {user_id} executed /role command")

        try:
            if self.role_manager is None:
                await message.answer(ROLE_ERROR_MESSAGE)
                return

            description = self.role_manager.get_role_description()
            await message.answer(description, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Error loading role for user {user_id}: {e}")
            await message.answer(ROLE_ERROR_MESSAGE)
