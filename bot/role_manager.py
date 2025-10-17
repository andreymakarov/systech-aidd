"""Управление ролью бота из файла"""


class RoleManager:
    """Управляет загрузкой и кэшированием роли бота из файла"""

    def __init__(self, role_file_path: str) -> None:
        """
        Инициализация менеджера ролей

        Args:
            role_file_path: Путь к файлу с описанием роли
        """
        self._role_file_path = role_file_path
        self._cached_role: str | None = None

    def load_role(self) -> str:
        """
        Загружает роль из файла (с кэшированием)

        Returns:
            Содержимое файла с ролью

        Raises:
            FileNotFoundError: Если файл не найден
            ValueError: Если файл пустой
        """
        # Возвращаем кэш, если уже загружали
        if self._cached_role is not None:
            return self._cached_role

        try:
            with open(self._role_file_path, encoding="utf-8") as f:
                role = f.read().strip()

            if not role:
                raise ValueError("Role file is empty")

            # Кэшируем загруженную роль
            self._cached_role = role
            return role

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Role file not found: {self._role_file_path}") from e

    def get_role_description(self) -> str:
        """
        Форматирует роль для отображения пользователю

        Returns:
            Отформатированное описание роли с эмодзи
        """
        role = self.load_role()
        return f"🎭 **Моя роль:**\n\n{role}"

