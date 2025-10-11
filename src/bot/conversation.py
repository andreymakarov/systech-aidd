class ConversationManager:
    """Управление историей диалогов в памяти"""

    def __init__(self) -> None:
        self.conversations: dict[int, list[dict[str, str]]] = {}

    def get_history(self, user_id: int) -> list[dict[str, str]]:
        """Получить историю диалога пользователя"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        return self.conversations[user_id]

    def add_message(self, user_id: int, role: str, content: str) -> None:
        """Добавить сообщение в историю диалога"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        self.conversations[user_id].append({"role": role, "content": content})

    def clear_history(self, user_id: int) -> None:
        """Очистить историю диалога пользователя"""
        if user_id in self.conversations:
            self.conversations[user_id] = []
