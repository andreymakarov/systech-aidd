"""Тесты для RoleManager"""

import pytest

from bot.role_manager import RoleManager


class TestRoleManager:
    """Тесты для класса RoleManager"""

    def test_load_role_from_file_success(self, tmp_path):
        """Успешная загрузка роли из файла"""
        # Arrange
        role_file = tmp_path / "test_role.txt"
        role_content = "Ты - тестовый ассистент для юнит-тестов."
        role_file.write_text(role_content, encoding="utf-8")

        role_manager = RoleManager(str(role_file))

        # Act
        result = role_manager.load_role()

        # Assert
        assert result == role_content

    def test_load_role_from_file_not_found(self, tmp_path):
        """Обработка отсутствующего файла"""
        # Arrange
        non_existent_file = tmp_path / "non_existent.txt"
        role_manager = RoleManager(str(non_existent_file))

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            role_manager.load_role()

        assert "non_existent.txt" in str(exc_info.value)

    def test_load_role_empty_file(self, tmp_path):
        """Обработка пустого файла"""
        # Arrange
        empty_file = tmp_path / "empty_role.txt"
        empty_file.write_text("", encoding="utf-8")

        role_manager = RoleManager(str(empty_file))

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            role_manager.load_role()

        assert "empty" in str(exc_info.value).lower()

    def test_load_role_whitespace_only_file(self, tmp_path):
        """Обработка файла только с пробелами"""
        # Arrange
        whitespace_file = tmp_path / "whitespace_role.txt"
        whitespace_file.write_text("   \n\t  \n  ", encoding="utf-8")

        role_manager = RoleManager(str(whitespace_file))

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            role_manager.load_role()

        assert "empty" in str(exc_info.value).lower()

    def test_get_role_description(self, tmp_path):
        """Получение описания роли для пользователя"""
        # Arrange
        role_file = tmp_path / "test_role.txt"
        role_content = "Ты - полезный ассистент."
        role_file.write_text(role_content, encoding="utf-8")

        role_manager = RoleManager(str(role_file))

        # Act
        description = role_manager.get_role_description()

        # Assert
        assert "🎭" in description  # Эмодзи маски
        assert role_content in description
        assert "роль" in description.lower()

    def test_role_caching(self, tmp_path):
        """Кэширование загруженной роли"""
        # Arrange
        role_file = tmp_path / "test_role.txt"
        initial_content = "Первоначальная роль"
        role_file.write_text(initial_content, encoding="utf-8")

        role_manager = RoleManager(str(role_file))

        # Act - первая загрузка
        first_load = role_manager.load_role()

        # Изменяем файл после первой загрузки
        role_file.write_text("Измененная роль", encoding="utf-8")

        # Вторая загрузка должна вернуть закешированное значение
        second_load = role_manager.load_role()

        # Assert
        assert first_load == initial_content
        assert second_load == initial_content  # Кэш должен сработать
        assert first_load == second_load

    def test_load_role_with_multiline_content(self, tmp_path):
        """Загрузка роли с многострочным содержимым"""
        # Arrange
        role_file = tmp_path / "multiline_role.txt"
        multiline_content = """Ты - помощник программиста.

Твои задачи:
- Помогать с кодом
- Отвечать на вопросы
- Быть полезным

Будь вежливым!"""
        role_file.write_text(multiline_content, encoding="utf-8")

        role_manager = RoleManager(str(role_file))

        # Act
        result = role_manager.load_role()

        # Assert
        assert result == multiline_content
        assert "Твои задачи:" in result
        assert "Будь вежливым!" in result

    def test_load_role_strips_trailing_whitespace(self, tmp_path):
        """Загрузка роли с удалением концевых пробелов"""
        # Arrange
        role_file = tmp_path / "role_with_whitespace.txt"
        content_with_whitespace = "  Ты - ассистент.  \n\n  "
        role_file.write_text(content_with_whitespace, encoding="utf-8")

        role_manager = RoleManager(str(role_file))

        # Act
        result = role_manager.load_role()

        # Assert
        assert result == "Ты - ассистент."
        assert not result.startswith(" ")
        assert not result.endswith(" ")
        assert not result.endswith("\n")




