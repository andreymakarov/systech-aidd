class ConversationManager:
    """Управление историей диалогов в памяти"""

    def __init__(self):
        self.conversations: dict[int, list[dict]] = {}

    def get_history(self, user_id: int) -> list[dict]:
        """Получить историю диалога пользователя"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        return self.conversations[user_id]

    def add_message(self, user_id: int, role: str, content: str):
        """Добавить сообщение в историю диалога"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []

        self.conversations[user_id].append({
            "role": role,
            "content": content
        })

